from django.contrib import admin

from apps.payments.models import Payment, PaymentWebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "provider",
        "provider_payment_id",
        "status",
        "amount",
        "refunded_amount",
        "created_at",
    )
    list_filter = ("provider", "status", "currency")
    search_fields = ("id", "provider_payment_id", "order__order_number")
    autocomplete_fields = ("order",)


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_id", "event_type", "is_processed", "created_at")
    list_filter = ("provider", "event_type", "is_processed")
    search_fields = ("event_id",)
