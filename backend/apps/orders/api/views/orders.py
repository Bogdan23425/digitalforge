from decimal import Decimal

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.orders.api.serializers.orders import (
    CartItemSerializer,
    CartItemWriteSerializer,
    CheckoutSerializer,
    OrderSerializer,
    CartSerializer,
)
from apps.orders.models import Order
from apps.orders.selectors import get_or_create_cart_for_user, get_user_orders
from apps.orders.services import (
    add_product_to_cart,
    clear_cart,
    create_checkout_order,
    remove_product_from_cart,
)
from apps.common.api.pagination import DefaultPageNumberPagination
from apps.common.api.serializers import DetailSerializer, ServiceHealthSerializer


class OrdersHealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(operation_id="orders_health", responses=ServiceHealthSerializer)
    def get(self, request):
        return Response({"service": "orders", "status": "ok"})


class CartView(APIView):
    @extend_schema(operation_id="cart_retrieve", responses={200: CartSerializer})
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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "cart_write"

    @extend_schema(
        operation_id="cart_items_create",
        request=CartItemWriteSerializer,
        responses={201: CartItemSerializer, 422: DetailSerializer},
    )
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

    @extend_schema(
        operation_id="cart_items_clear",
        request=None,
        responses={204: OpenApiResponse(description="Cart cleared.")},
    )
    def delete(self, request):
        clear_cart(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemDeleteView(APIView):
    @extend_schema(
        operation_id="cart_item_delete",
        request=None,
        responses={
            204: OpenApiResponse(description="Cart item removed."),
            404: DetailSerializer,
        },
    )
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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "checkout"

    @extend_schema(
        operation_id="checkout_create",
        request=CheckoutSerializer,
        responses={201: OrderSerializer, 422: DetailSerializer},
    )
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


class OrderListView(GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.none()
    pagination_class = DefaultPageNumberPagination

    @extend_schema(
        operation_id="orders_list", responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        orders = get_user_orders(user=request.user)
        page = self.paginate_queryset(orders)
        if page is not None:
            return self.get_paginated_response(OrderSerializer(page, many=True).data)
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    @extend_schema(
        operation_id="orders_detail",
        responses={200: OrderSerializer, 404: DetailSerializer},
    )
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
