from rest_framework import serializers

from apps.catalog.models import Product
from apps.orders.models import CartItem, Order


class CartItemWriteSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
    )


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    title = serializers.CharField(source="product.title", read_only=True)
    price = serializers.DecimalField(
        source="product.base_price", max_digits=10, decimal_places=2, read_only=True
    )
    currency = serializers.CharField(source="product.currency", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "title", "price", "currency", "created_at"]


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()


class CheckoutSerializer(serializers.Serializer):
    payment_provider = serializers.CharField(default="stripe")


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    title = serializers.CharField(source="product.title", read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    platform_fee_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    seller_net_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "subtotal_amount",
            "platform_fee_amount",
            "total_amount",
            "currency",
            "items",
            "created_at",
        ]
