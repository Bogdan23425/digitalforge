from apps.orders.models import Order


def get_user_orders(*, user):
    return (
        Order.objects.filter(buyer=user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
