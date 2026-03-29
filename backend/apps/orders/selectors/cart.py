from apps.orders.models import Cart


def get_or_create_cart_for_user(*, user):
    return Cart.objects.get_or_create(user=user)
