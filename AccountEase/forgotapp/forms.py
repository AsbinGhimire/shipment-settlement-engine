from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
import logging

# -----------------------------
# LOGGER SETUP
# -----------------------------
logger = logging.getLogger(__name__)

# -----------------------------------
# FORGOT PASSWORD (EMAIL)
# -----------------------------------
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email",
            "class": "input"
        })
    )


# -----------------------------------
# VERIFY OTP
# -----------------------------------
class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter 6-digit OTP",
            "class": "input",
            "inputmode": "numeric"
        })
    )


# -----------------------------------
# RESET PASSWORD
# -----------------------------------
class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "New Password",
            "class": "input"
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm Password",
            "class": "input"
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password:
            # Check minimum length
            if len(password) < 8:
                logger.warning("Password too short")
                raise ValidationError("Password must be at least 8 characters long.")

            # Check for letters + numbers OR letters + symbols
            has_letter = bool(re.search(r"[A-Za-z]", password))
            has_number = bool(re.search(r"\d", password))
            has_symbol = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

            if not ((has_letter and has_number) or (has_letter and has_symbol)):
                logger.warning("Password does not meet complexity requirements")
                raise ValidationError(
                    "Password must contain letters and numbers or letters and symbols."
                )

            # Apply Django's built-in validators
            try:
                validate_password(password)
            except ValidationError as e:
                logger.warning(f"Password validation failed: {e.messages}")
                raise

            logger.info("Password passed validation checks")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                logger.warning("Passwords do not match in ResetPasswordForm")
                raise ValidationError("Passwords do not match.")

        return cleaned_data


# # forgotapp/forms.py

# from django import forms
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError


# # -----------------------------------
# # FORGOT PASSWORD (EMAIL)
# # -----------------------------------
# class ForgotPasswordForm(forms.Form):
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={
#             "placeholder": "Enter your email",
#             "class": "input"
#         })
#     )


# # -----------------------------------
# # VERIFY OTP
# # -----------------------------------
# class VerifyOTPForm(forms.Form):
#     otp = forms.CharField(
#         max_length=6,
#         min_length=6,
#         widget=forms.TextInput(attrs={
#             "placeholder": "Enter 6-digit OTP",
#             "class": "input",
#             "inputmode": "numeric"
#         })
#     )


# # -----------------------------------
# # RESET PASSWORD
# # -----------------------------------
# # 

# from django import forms
# from django.core.exceptions import ValidationError
# from django.contrib.auth.password_validation import validate_password
# import re

# class ResetPasswordForm(forms.Form):
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             "placeholder": "New Password",
#             "class": "input"
#         })
#     )

#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             "placeholder": "Confirm Password",
#             "class": "input"
#         })
#     )

#     def clean_password(self):
#         password = self.cleaned_data.get("password")

#         if password:
#             # Check minimum length
#             if len(password) < 8:
#                 raise ValidationError("Password must be at least 8 characters long.")

#             # Check for letters + numbers OR letters + symbols
#             has_letter = bool(re.search(r"[A-Za-z]", password))
#             has_number = bool(re.search(r"\d", password))
#             has_symbol = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

#             if not ((has_letter and has_number) or (has_letter and has_symbol)):
#                 raise ValidationError(
#                     "Password must contain letters and numbers or letters and symbols."
#                 )

#             # Apply Django's built-in validators
#             validate_password(password)

#         return password

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password and confirm_password:
#             if password != confirm_password:
#                 raise ValidationError("Passwords do not match.")

#         return cleaned_data

