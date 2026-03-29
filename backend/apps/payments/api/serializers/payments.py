from decimal import Decimal

from rest_framework import serializers

from apps.payments.models import Payment


class PaymentActionSerializer(serializers.Serializer):
    provider_payment_id = serializers.CharField(required=False, allow_blank=True)


class PaymentRefundSerializer(serializers.Serializer):
    refunded_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal("0.00"),
    )


class PaymentWebhookSerializer(serializers.Serializer):
    provider = serializers.CharField(default="stripe")
    event_id = serializers.CharField()
    event_type = serializers.ChoiceField(
        choices=[
            "payment.processing",
            "payment.succeeded",
            "payment.failed",
            "payment.partially_refunded",
            "payment.refunded",
        ]
    )
    payment_id = serializers.UUIDField(required=False)
    provider_payment_id = serializers.CharField(required=False, allow_blank=True)
    payload = serializers.JSONField(required=False, default=dict)
    refunded_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal("0.00"),
    )

    def validate(self, attrs):
        if not attrs.get("payment_id") and not attrs.get("provider_payment_id"):
            raise serializers.ValidationError(
                "Either payment_id or provider_payment_id is required."
            )
        if attrs["event_type"] in {"payment.partially_refunded", "payment.refunded"}:
            if attrs.get("refunded_amount") is None:
                raise serializers.ValidationError(
                    "refunded_amount is required for refund events."
                )
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order.id", read_only=True)
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    order_status = serializers.CharField(source="order.status", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "order_number",
            "order_status",
            "provider",
            "provider_payment_id",
            "status",
            "amount",
            "currency",
            "refunded_amount",
            "created_at",
            "updated_at",
        ]
