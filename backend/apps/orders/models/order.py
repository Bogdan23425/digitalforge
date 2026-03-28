from django.conf import settings
from django.db import models

from apps.common.choices import OrderStatus
from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Order(UUIDPrimaryKeyModel, TimestampedModel):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=40, unique=True)
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
    )
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")


class OrderItem(UUIDPrimaryKeyModel, TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sold_order_items",
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    seller_net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"], name="uq_order_product"
            )
        ]
