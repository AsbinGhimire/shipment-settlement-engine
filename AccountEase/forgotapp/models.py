from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

User = get_user_model()

# -----------------------------
# LOGGER SETUP
# -----------------------------
logger = logging.getLogger(__name__)


class PasswordResetOTP(models.Model):
    """
    Model to store One-Time Passwords (OTPs) for password reset functionality.
    Links an OTP to a specific user and tracks usage/expiration.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp', 'is_used']),
        ]

    def is_expired(self):
        """
        Check if the OTP has expired (valid for 10 minutes).
        Returns True if expired, False otherwise.
        """
        expired = timezone.now() > self.created_at + timezone.timedelta(minutes=10)
        if expired:
            logger.info(f"OTP {self.otp} for user {self.user.email} has expired")
        return expired

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
