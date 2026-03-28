from django.db import models

from apps.common.choices import PaymentStatus
from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Payment(UUIDPrimaryKeyModel, TimestampedModel):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    provider = models.CharField(max_length=32, default="stripe")
    provider_payment_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.INITIATED,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class PaymentWebhookEvent(UUIDPrimaryKeyModel, TimestampedModel):
    provider = models.CharField(max_length=50)
    event_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    is_processed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "event_id"], name="uq_provider_event_id"
            )
        ]
