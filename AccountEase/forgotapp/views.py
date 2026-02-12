import random
import logging
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import PasswordResetOTP
from .forms import ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm

User = get_user_model()

# -----------------------------
# LOGGER SETUP
# -----------------------------
logger = logging.getLogger(__name__)

# -------------------------------------------------
# FORGOT PASSWORD (SEND OTP)
# -------------------------------------------------
def forgot_password(request):
    """
    Handles the initial step of password recovery.
    - Validates the email address.
    - Generates a 6-digit OTP.
    - Sends the OTP via email.
    """
    form = ForgotPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        logger.info(f"Password reset requested for email: {email}")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"No user found for email: {email}")
            messages.error(request, "No account found with this email.")
            return redirect("forgotapp:forgot_pswd")

        # Invalidate previous OTPs
        updated_count = PasswordResetOTP.objects.filter(
            user=user, is_used=False
        ).update(is_used=True)
        logger.debug(f"Marked {updated_count} previous OTPs as used for {user.email}")

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)
        logger.info(f"Generated OTP {otp} for user {user.email}")

        # Send OTP email
        try:
            send_mail(
                subject="Your Password Reset OTP",
                message=f"Your OTP is {otp}. It expires in 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Sent OTP email to {email}")
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}")
            messages.warning(request, "OTP generated, but email failed to send.")

        # Reset session safely
        request.session.flush()
        request.session["reset_user_id"] = user.id
        logger.debug(f"Stored reset_user_id in session for user {user.email}")

        messages.success(request, "OTP sent to your email.")
        return redirect("forgotapp:verify_otp")

    return render(request, "forgotapp/forgot_pswd.html", {"form": form})


# -------------------------------------------------
# VERIFY OTP
# -------------------------------------------------
def verify_otp(request):
    """
    Verifies the OTP entered by the user.
    - Checks if OTP matches the one stored for the session user.
    - Checks for expiration.
    - Marks OTP as used upon success.
    """
    user_id = request.session.get("reset_user_id")
    if not user_id:
        logger.warning("OTP verification attempted without a reset_user_id in session")
        return redirect("forgotapp:forgot_pswd")

    form = VerifyOTPForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        otp_input = form.cleaned_data["otp"]
        logger.info(f"Verifying OTP {otp_input} for user_id {user_id}")

        otp_obj = PasswordResetOTP.objects.filter(
            user_id=user_id,
            otp=otp_input,
            is_used=False
        ).last()

        if not otp_obj:
            logger.warning(f"Invalid OTP {otp_input} attempt for user_id {user_id}")
            messages.error(request, "Invalid OTP.")
            return redirect("forgotapp:verify_otp")

        if otp_obj.is_expired():
            otp_obj.is_used = True
            otp_obj.save()
            logger.info(f"Expired OTP {otp_input} used for user_id {user_id}")
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect("forgotapp:forgot_pswd")

        otp_obj.is_used = True
        otp_obj.save()
        request.session["otp_verified"] = True
        logger.info(f"OTP {otp_input} verified successfully for user_id {user_id}")

        messages.success(request, "OTP verified. Set your new password.")
        return redirect("forgotapp:reset_password")

    return render(request, "forgotapp/verify_otp.html", {"form": form})


# -------------------------------------------------
# RESET PASSWORD
# -------------------------------------------------
def reset_password(request):
    """
    Final step: Set the new password.
    - Requires 'reset_user_id' and 'otp_verified' in session.
    - Updates user password safely.
    - Clears sensitive session data and unused OTPs.
    """
    user_id = request.session.get("reset_user_id")
    otp_verified = request.session.get("otp_verified")

    if not user_id or not otp_verified:
        logger.warning("Reset password attempted without proper session verification")
        return redirect("forgotapp:forgot_pswd")

    form = ResetPasswordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            password = form.cleaned_data["password"]

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"User not found for reset_user_id {user_id}")
                request.session.flush()
                return redirect("forgotapp:forgot_pswd")

            # Reset password safely
            with transaction.atomic():
                user.set_password(password)
                user.save()
                PasswordResetOTP.objects.filter(user=user).delete()
                logger.info(f"Password reset successfully for user {user.email}")

            # Clear session
            request.session.flush()
            messages.success(request, "Password reset successfully. You can now log in.")
            login_url = f"{reverse('login')}?reset_success=1"
            return redirect(login_url)

        else:
            logger.warning(f"Reset password form invalid for user_id {user_id}")
            form.add_error(None, "Please correct the errors below.")

    return render(request, "forgotapp/reset_password.html", {"form": form})
