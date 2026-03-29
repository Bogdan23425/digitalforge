from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from apps.common.choices import OrderStatus, PaymentStatus
from apps.common.choices import ProductStatus
from apps.library.models import PurchaseAccess
from apps.orders.models import Order, OrderItem
from apps.orders.selectors import get_or_create_cart_for_user
from apps.payments.models import Payment

PLATFORM_FEE_RATE = Decimal("0.10")


def _generate_order_number() -> str:
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:6].upper()
    return f"ORD-{timestamp}-{suffix}"


@transaction.atomic
def create_checkout_order(*, user, payment_provider: str = "stripe") -> Order:
    cart, _ = get_or_create_cart_for_user(user=user)
    cart_items = list(cart.items.select_related("product", "product__seller"))
    if not cart_items:
        raise ValueError("Cart is empty.")

    subtotal = Decimal("0.00")
    platform_fee = Decimal("0.00")
    order = Order.objects.create(
        buyer=user,
        order_number=_generate_order_number(),
        status=OrderStatus.PENDING_PAYMENT,
        subtotal_amount=Decimal("0.00"),
        platform_fee_amount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        currency="USD",
    )

    for cart_item in cart_items:
        product = cart_item.product
        if product.status != ProductStatus.PUBLISHED:
            raise ValueError("Checkout contains an unpublished product.")
        if product.seller_id == user.id:
            raise ValueError("You cannot purchase your own product.")
        if PurchaseAccess.objects.filter(
            buyer=user, product=product, is_active=True
        ).exists():
            raise ValueError("Checkout contains a product you already own.")
        item_price = product.base_price
        item_fee = (item_price * PLATFORM_FEE_RATE).quantize(Decimal("0.01"))
        subtotal += item_price
        platform_fee += item_fee
        OrderItem.objects.create(
            order=order,
            product=product,
            seller=product.seller,
            unit_price=item_price,
            final_price=item_price,
            platform_fee_amount=item_fee,
            seller_net_amount=(item_price - item_fee).quantize(Decimal("0.01")),
        )

    order.subtotal_amount = subtotal
    order.platform_fee_amount = platform_fee
    order.total_amount = subtotal
    order.save(
        update_fields=[
            "subtotal_amount",
            "platform_fee_amount",
            "total_amount",
            "updated_at",
        ]
    )

    Payment.objects.create(
        order=order,
        provider=payment_provider,
        status=PaymentStatus.INITIATED,
        amount=order.total_amount,
        currency=order.currency,
    )

    cart.items.all().delete()
    return order
