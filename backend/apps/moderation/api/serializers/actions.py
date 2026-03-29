from rest_framework import serializers

from apps.catalog.models import Product


class ModerationQueueItemSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "product_type",
            "base_price",
            "currency",
            "moderation_note",
            "seller",
            "category",
            "created_at",
            "updated_at",
        ]

    def get_seller(self, obj):
        return {
            "id": str(obj.seller_id),
            "email": obj.seller.email,
            "username": obj.seller.username,
        }

    def get_category(self, obj):
        return {
            "id": str(obj.category_id),
            "name": obj.category.name,
            "slug": obj.category.slug,
        }


class ModerationActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
