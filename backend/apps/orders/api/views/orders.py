from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.api.serializers.orders import (
    CartItemSerializer,
    CartItemWriteSerializer,
    CheckoutSerializer,
    OrderSerializer,
)
from apps.orders.models import Order
from apps.orders.selectors import get_or_create_cart_for_user, get_user_orders
from apps.orders.services import (
    add_product_to_cart,
    clear_cart,
    create_checkout_order,
    remove_product_from_cart,
)


class OrdersHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"service": "orders", "status": "ok"})


class CartView(APIView):
    def get(self, request):
        cart, _ = get_or_create_cart_for_user(user=request.user)
        items = list(cart.items.select_related("product").order_by("-created_at"))
        subtotal = sum((item.product.base_price for item in items), Decimal("0.00"))
        return Response(
            {
                "items": CartItemSerializer(items, many=True).data,
                "subtotal": f"{subtotal:.2f}",
                "total": f"{subtotal:.2f}",
                "currency": "USD",
            }
        )


class CartItemListCreateView(APIView):
    def post(self, request):
        serializer = CartItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item, _ = add_product_to_cart(
                user=request.user,
                product=serializer.validated_data["product"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        clear_cart(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemDeleteView(APIView):
    def delete(self, request, product_id):
        from apps.catalog.models import Product

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        remove_product_from_cart(user=request.user, product=product)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_checkout_order(
                user=request.user,
                payment_provider=serializer.validated_data["payment_provider"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(APIView):
    def get(self, request):
        orders = get_user_orders(user=request.user)
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    def get(self, request, pk):
        try:
            order = Order.objects.prefetch_related("items__product").get(
                pk=pk, buyer=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(OrderSerializer(order).data)
