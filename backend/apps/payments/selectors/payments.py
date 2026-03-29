from apps.payments.models import Payment


def get_user_payments(*, user):
    return (
        Payment.objects.select_related("order")
        .filter(order__buyer=user)
        .order_by("-created_at")
    )


def get_user_payment_by_id(*, user, payment_id):
    return (
        Payment.objects.select_related("order")
        .filter(
            id=payment_id,
            order__buyer=user,
        )
        .first()
    )


def get_payment_for_webhook(*, provider: str, payment_id=None, provider_payment_id=""):
    queryset = Payment.objects.select_related("order")
    if payment_id:
        payment = queryset.filter(id=payment_id).first()
        if payment is not None:
            return payment
    if provider_payment_id:
        return queryset.filter(
            provider=provider,
            provider_payment_id=provider_payment_id,
        ).first()
    return None
