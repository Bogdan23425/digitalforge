from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class ProductImage(UUIDPrimaryKeyModel, TimestampedModel):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image_url = models.URLField()
    kind = models.CharField(max_length=16, default="gallery")
    sort_order = models.PositiveIntegerField(default=0)
