from django.db import models

from apps.common.choices import FileScanStatus
from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class ProductFile(UUIDPrimaryKeyModel, TimestampedModel):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="files",
    )
    file_name = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=500, unique=True)
    mime_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    checksum = models.CharField(max_length=128, blank=True)
    is_current = models.BooleanField(default=True)
    scan_status = models.CharField(
        max_length=16,
        choices=FileScanStatus.choices,
        default=FileScanStatus.PENDING,
    )
