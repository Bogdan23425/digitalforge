from django.conf import settings
from django.db import models

from apps.common.choices import ProductStatus
from apps.common.db.models import SoftDeleteModel, TimestampedModel, UUIDPrimaryKeyModel


class Product(UUIDPrimaryKeyModel, TimestampedModel, SoftDeleteModel):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="products",
    )
    category = models.ForeignKey(
        "catalog.Category",
        on_delete=models.PROTECT,
        related_name="products",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    short_description = models.CharField(max_length=500)
    full_description = models.TextField()
    product_type = models.CharField(max_length=50, default="other")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=32,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
    )
    moderation_note = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
