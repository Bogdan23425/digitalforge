from decimal import Decimal

import stripe
from django.conf import settings

from apps.payments.services.webhooks import process_payment_webhook

STRIPE_EVENT_TYPE_MAP = {
    "payment_intent.processing": "payment.processing",
    "payment_intent.succeeded": "payment.succeeded",
    "payment_intent.payment_failed": "payment.failed",
}


def _normalize_refunded_amount(amount: int | None) -> Decimal | None:
    if amount is None:
        return None
    return (Decimal(amount) / Decimal("100")).quantize(Decimal("0.01"))


def _extract_charge_refund_data(event: dict) -> dict:
    charge = event["data"]["object"]
    metadata = charge.get("metadata") or {}
    amount_refunded = _normalize_refunded_amount(charge.get("amount_refunded", 0))
    amount = _normalize_refunded_amount(charge.get("amount"))
    event_type = (
        "payment.refunded"
        if amount is not None and amount_refunded == amount
        else "payment.partially_refunded"
    )
    return {
        "event_type": event_type,
        "payment_id": metadata.get("payment_id"),
        "provider_payment_id": charge.get("payment_intent") or charge.get("id", ""),
        "refunded_amount": amount_refunded,
    }


def build_internal_event_from_stripe(*, event: dict) -> dict:
    stripe_event_type = event["type"]
    if stripe_event_type == "charge.refunded":
        return _extract_charge_refund_data(event)
    if stripe_event_type not in STRIPE_EVENT_TYPE_MAP:
        raise ValueError(f"Unsupported Stripe event type '{stripe_event_type}'.")

    payment_intent = event["data"]["object"]
    metadata = payment_intent.get("metadata") or {}
    return {
        "event_type": STRIPE_EVENT_TYPE_MAP[stripe_event_type],
        "payment_id": metadata.get("payment_id"),
        "provider_payment_id": payment_intent.get("id", ""),
        "refunded_amount": None,
    }


def verify_and_process_stripe_webhook(*, payload: bytes, signature: str):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise ValueError("Stripe webhook secret is not configured.")

    event = stripe.Webhook.construct_event(
        payload=payload,
        sig_header=signature,
        secret=settings.STRIPE_WEBHOOK_SECRET,
    )
    internal_event = build_internal_event_from_stripe(event=event)
    return process_payment_webhook(
        provider="stripe",
        event_id=event["id"],
        event_type=internal_event["event_type"],
        payload=event,
        payment_id=internal_event.get("payment_id"),
        provider_payment_id=internal_event["provider_payment_id"],
        refunded_amount=internal_event["refunded_amount"],
    )
