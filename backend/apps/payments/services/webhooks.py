from django.db import IntegrityError, transaction

from apps.payments.models import PaymentWebhookEvent
from apps.payments.selectors.payments import get_payment_for_webhook
from apps.payments.services.payments import (
    mark_payment_failed,
    mark_payment_partially_refunded,
    mark_payment_processing,
    mark_payment_refunded,
    mark_payment_succeeded,
)


def _get_or_create_webhook_event(*, provider: str, event_id: str, defaults: dict):
    try:
        return PaymentWebhookEvent.objects.get_or_create(
            provider=provider,
            event_id=event_id,
            defaults=defaults,
        )
    except IntegrityError:
        event = PaymentWebhookEvent.objects.get(provider=provider, event_id=event_id)
        return event, False


@transaction.atomic
def process_payment_webhook(
    *,
    provider: str,
    event_id: str,
    event_type: str,
    payload: dict,
    payment_id=None,
    provider_payment_id: str = "",
    refunded_amount=None,
):
    event, created = _get_or_create_webhook_event(
        provider=provider,
        event_id=event_id,
        defaults={"event_type": event_type, "payload": payload},
    )

    if not created:
        if event.is_processed:
            payment = get_payment_for_webhook(
                provider=provider,
                payment_id=payment_id,
                provider_payment_id=provider_payment_id,
            )
            return {
                "event": event,
                "payment": payment,
                "created": False,
                "processed": False,
            }
        event.event_type = event_type
        event.payload = payload
        event.save(update_fields=["event_type", "payload", "updated_at"])

    payment = get_payment_for_webhook(
        provider=provider,
        payment_id=payment_id,
        provider_payment_id=provider_payment_id,
    )
    if payment is None:
        raise ValueError("Payment not found for webhook event.")

    if event_type == "payment.processing":
        payment = mark_payment_processing(
            payment=payment,
            provider_payment_id=provider_payment_id,
        )
    elif event_type == "payment.succeeded":
        payment = mark_payment_succeeded(
            payment=payment,
            provider_payment_id=provider_payment_id,
        )
    elif event_type == "payment.failed":
        payment = mark_payment_failed(payment=payment)
    elif event_type == "payment.partially_refunded":
        payment = mark_payment_partially_refunded(
            payment=payment,
            refunded_amount=refunded_amount,
        )
    elif event_type == "payment.refunded":
        payment = mark_payment_refunded(
            payment=payment,
            refunded_amount=refunded_amount,
        )
    else:
        raise ValueError(f"Unsupported payment event type '{event_type}'.")

    event.is_processed = True
    event.save(update_fields=["is_processed", "updated_at"])
    return {"event": event, "payment": payment, "created": created, "processed": True}
