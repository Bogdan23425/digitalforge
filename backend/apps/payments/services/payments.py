from decimal import Decimal

from apps.audit.services import write_audit_log
from django.db import transaction
from django.utils import timezone

from apps.common.choices import OrderStatus, PaymentStatus
from apps.library.models import PurchaseAccess
from apps.notifications.services import create_notification


def _ensure_payment_can_transition(payment, *, allowed_statuses: set[str]) -> None:
    if payment.status not in allowed_statuses:
        raise ValueError(f"Payment cannot be updated from status '{payment.status}'.")


def _revoke_purchase_accesses(*, payment):
    PurchaseAccess.objects.filter(
        order_item__order=payment.order,
        is_active=True,
    ).update(is_active=False, revoked_at=timezone.now())


@transaction.atomic
def mark_payment_processing(*, payment, provider_payment_id: str = ""):
    if payment.status == PaymentStatus.PROCESSING:
        return payment
    if payment.status in {
        PaymentStatus.SUCCEEDED,
        PaymentStatus.FAILED,
        PaymentStatus.CANCELED,
        PaymentStatus.REFUNDED,
        PaymentStatus.PARTIALLY_REFUNDED,
        PaymentStatus.DISPUTED,
    }:
        raise ValueError(f"Payment cannot be updated from status '{payment.status}'.")

    payment.status = PaymentStatus.PROCESSING
    if provider_payment_id:
        payment.provider_payment_id = provider_payment_id
    payment.save(update_fields=["status", "provider_payment_id", "updated_at"])
    payment.refresh_from_db()
    return payment


@transaction.atomic
def mark_payment_partially_refunded(*, payment, refunded_amount):
    refunded_amount = Decimal(refunded_amount)
    if refunded_amount <= Decimal("0.00"):
        raise ValueError("refunded_amount must be greater than zero.")
    if refunded_amount > payment.amount:
        raise ValueError("refunded_amount cannot exceed payment amount.")
    if refunded_amount == payment.amount:
        return mark_payment_refunded(payment=payment, refunded_amount=refunded_amount)
    if payment.status not in {
        PaymentStatus.SUCCEEDED,
        PaymentStatus.PARTIALLY_REFUNDED,
    }:
        raise ValueError(f"Payment cannot be updated from status '{payment.status}'.")
    if refunded_amount < payment.refunded_amount:
        raise ValueError(
            "refunded_amount cannot be less than the existing refunded amount."
        )
    if refunded_amount == payment.refunded_amount:
        return payment

    payment.status = PaymentStatus.PARTIALLY_REFUNDED
    payment.refunded_amount = refunded_amount
    payment.save(update_fields=["status", "refunded_amount", "updated_at"])

    order = payment.order
    order.status = OrderStatus.PARTIALLY_REFUNDED
    order.save(update_fields=["status", "updated_at"])
    create_notification(
        user=order.buyer,
        notification_type="payment.partially_refunded",
        title="Partial refund issued",
        body=(
            f"A partial refund of {payment.refunded_amount} {payment.currency} "
            f"was issued for order {order.order_number}."
        ),
    )
    write_audit_log(
        actor_user=order.buyer,
        action_type="payment.partially_refunded",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"refunded_amount": str(payment.refunded_amount)},
    )

    payment.refresh_from_db()
    return payment


@transaction.atomic
def mark_payment_refunded(*, payment, refunded_amount=None):
    refunded_amount = (
        payment.amount if refunded_amount is None else Decimal(refunded_amount)
    )
    if refunded_amount != payment.amount:
        raise ValueError("Full refund must match the full payment amount.")
    if payment.status == PaymentStatus.REFUNDED:
        return payment
    if payment.status not in {
        PaymentStatus.SUCCEEDED,
        PaymentStatus.PARTIALLY_REFUNDED,
    }:
        raise ValueError(f"Payment cannot be updated from status '{payment.status}'.")

    payment.status = PaymentStatus.REFUNDED
    payment.refunded_amount = payment.amount
    payment.save(update_fields=["status", "refunded_amount", "updated_at"])

    order = payment.order
    order.status = OrderStatus.REFUNDED
    order.save(update_fields=["status", "updated_at"])

    _revoke_purchase_accesses(payment=payment)
    create_notification(
        user=order.buyer,
        notification_type="payment.refunded",
        title="Refund issued",
        body=f"Your order {order.order_number} was fully refunded.",
    )
    write_audit_log(
        actor_user=order.buyer,
        action_type="payment.refunded",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"refunded_amount": str(payment.refunded_amount)},
    )

    payment.refresh_from_db()
    return payment


@transaction.atomic
def mark_payment_succeeded(*, payment, provider_payment_id: str = ""):
    if payment.status == PaymentStatus.SUCCEEDED:
        if provider_payment_id and not payment.provider_payment_id:
            payment.provider_payment_id = provider_payment_id
            payment.save(update_fields=["provider_payment_id", "updated_at"])
            payment.refresh_from_db()
        return payment
    _ensure_payment_can_transition(
        payment,
        allowed_statuses={PaymentStatus.INITIATED, PaymentStatus.PROCESSING},
    )

    payment.status = PaymentStatus.SUCCEEDED
    if provider_payment_id:
        payment.provider_payment_id = provider_payment_id
    payment.save(update_fields=["status", "provider_payment_id", "updated_at"])

    order = payment.order
    order.status = OrderStatus.PAID
    order.save(update_fields=["status", "updated_at"])

    for order_item in order.items.select_related("product").all():
        PurchaseAccess.objects.get_or_create(
            buyer=order.buyer,
            product=order_item.product,
            defaults={"order_item": order_item, "is_active": True},
        )

    order.status = OrderStatus.FULFILLED
    order.save(update_fields=["status", "updated_at"])
    create_notification(
        user=order.buyer,
        notification_type="payment.succeeded",
        title="Payment succeeded",
        body=f"Your payment for order {order.order_number} was confirmed.",
    )
    write_audit_log(
        actor_user=order.buyer,
        action_type="payment.succeeded",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"order_number": order.order_number},
    )

    payment.refresh_from_db()
    return payment


@transaction.atomic
def mark_payment_failed(*, payment):
    if payment.status == PaymentStatus.FAILED:
        return payment
    _ensure_payment_can_transition(
        payment,
        allowed_statuses={PaymentStatus.INITIATED, PaymentStatus.PROCESSING},
    )

    payment.status = PaymentStatus.FAILED
    payment.save(update_fields=["status", "updated_at"])

    order = payment.order
    order.status = OrderStatus.FAILED
    order.save(update_fields=["status", "updated_at"])
    create_notification(
        user=order.buyer,
        notification_type="payment.failed",
        title="Payment failed",
        body=f"Your payment for order {order.order_number} failed.",
    )
    write_audit_log(
        actor_user=order.buyer,
        action_type="payment.failed",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"order_number": order.order_number},
    )

    payment.refresh_from_db()
    return payment
