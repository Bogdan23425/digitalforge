from django.conf import settings
from django.db import models

from apps.common.db.models import UUIDPrimaryKeyModel


class EmailVerificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    VERIFIED = "verified", "Verified"
    EXPIRED = "expired", "Expired"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"


class EmailVerification(UUIDPrimaryKeyModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verifications",
    )
    code_hash = models.CharField(max_length=255)
    status = models.CharField(
        max_length=16,
        choices=EmailVerificationStatus.choices,
        default=EmailVerificationStatus.PENDING,
    )
    attempts_count = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    resend_available_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
