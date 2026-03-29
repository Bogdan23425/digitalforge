from django.db import IntegrityError, transaction

from apps.catalog.models import Product
from apps.common.choices import ProductStatus
from apps.library.models import PurchaseAccess
from apps.orders.models import CartItem
from apps.orders.selectors import get_or_create_cart_for_user


def _validate_product_for_cart(*, user, product: Product) -> None:
    if product.status != ProductStatus.PUBLISHED:
        raise ValueError("Only published products can be added to the cart.")
    if product.seller_id == user.id:
        raise ValueError("You cannot buy your own product.")
    if PurchaseAccess.objects.filter(
        buyer=user, product=product, is_active=True
    ).exists():
        raise ValueError("You already own this product.")


@transaction.atomic
def add_product_to_cart(*, user, product: Product):
    _validate_product_for_cart(user=user, product=product)
    cart, _ = get_or_create_cart_for_user(user=user)
    if CartItem.objects.filter(cart=cart, product=product).exists():
        raise ValueError("Product is already in the cart.")
    try:
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    except IntegrityError:
        raise ValueError("Product is already in the cart.")
    return item, created


@transaction.atomic
def remove_product_from_cart(*, user, product: Product) -> None:
    cart, _ = get_or_create_cart_for_user(user=user)
    CartItem.objects.filter(cart=cart, product=product).delete()


@transaction.atomic
def clear_cart(*, user) -> None:
    cart, _ = get_or_create_cart_for_user(user=user)
    cart.items.all().delete()
