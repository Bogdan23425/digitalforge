from django.conf import settings
from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Cart(UUIDPrimaryKeyModel, TimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )


class CartItem(UUIDPrimaryKeyModel, TimestampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="uq_cart_product")
        ]
