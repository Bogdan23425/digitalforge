from django.contrib import admin

from apps.orders.models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__email", "user__username")
    autocomplete_fields = ("user",)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product", "seller")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "buyer",
        "status",
        "total_amount",
        "currency",
        "created_at",
    )
    list_filter = ("status", "currency")
    search_fields = ("order_number", "buyer__email", "buyer__username")
    autocomplete_fields = ("buyer",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "seller",
        "final_price",
        "platform_fee_amount",
        "seller_net_amount",
        "created_at",
    )
    search_fields = (
        "order__order_number",
        "product__title",
        "product__slug",
        "seller__email",
        "seller__username",
    )
    autocomplete_fields = ("order", "product", "seller")
