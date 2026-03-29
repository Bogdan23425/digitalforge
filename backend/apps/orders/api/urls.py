from django.urls import path

from apps.orders.api.views import (
    CartItemDeleteView,
    CartItemListCreateView,
    CartView,
    CheckoutView,
    OrderDetailView,
    OrderListView,
    OrdersHealthView,
)

urlpatterns = [
    path("health/", OrdersHealthView.as_view(), name="orders-health"),
    path("cart/", CartView.as_view(), name="cart-detail"),
    path("cart/items/", CartItemListCreateView.as_view(), name="cart-items"),
    path(
        "cart/items/<uuid:product_id>/",
        CartItemDeleteView.as_view(),
        name="cart-item-delete",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
