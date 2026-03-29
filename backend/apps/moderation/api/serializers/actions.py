from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.catalog.models import Product


class ModerationSellerSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)


class ModerationCategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)


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

    @extend_schema_field(ModerationSellerSerializer)
    def get_seller(self, obj) -> dict:
        return {
            "id": str(obj.seller_id),
            "email": obj.seller.email,
            "username": obj.seller.username,
        }

    @extend_schema_field(ModerationCategorySerializer)
    def get_category(self, obj) -> dict:
        return {
            "id": str(obj.category_id),
            "name": obj.category.name,
            "slug": obj.category.slug,
        }


class ModerationActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
