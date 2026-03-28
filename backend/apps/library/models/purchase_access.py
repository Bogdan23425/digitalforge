from django.conf import settings
from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class PurchaseAccess(UUIDPrimaryKeyModel, TimestampedModel):
    order_item = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.CASCADE,
        related_name="purchase_accesses",
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchase_accesses",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="purchase_accesses",
    )
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["buyer", "product"], name="uq_buyer_product_access"
            )
        ]
