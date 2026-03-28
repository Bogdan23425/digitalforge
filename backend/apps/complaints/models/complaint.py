from django.conf import settings
from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Complaint(UUIDPrimaryKeyModel, TimestampedModel):
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaints",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="complaints",
    )
    status = models.CharField(max_length=32, default="open")
    reason = models.CharField(max_length=100)
    details = models.TextField(blank=True)
