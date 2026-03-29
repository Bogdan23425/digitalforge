from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.catalog.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "sort_order", "is_active"]


class PublicSellerSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(read_only=True)


class PublicProductImageSerializer(serializers.Serializer):
    image_url = serializers.URLField(read_only=True)
    kind = serializers.CharField(read_only=True)
    sort_order = serializers.IntegerField(read_only=True)


class PublicProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = PublicSellerSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "product_type",
            "base_price",
            "currency",
            "category",
            "seller",
            "cover_image_url",
            "published_at",
        ]

    @extend_schema_field(serializers.URLField(allow_blank=True))
    def get_cover_image_url(self, obj) -> str:
        cover_image = (
            obj.images.filter(kind="cover").order_by("sort_order", "created_at").first()
        )
        return cover_image.image_url if cover_image else ""


class PublicProductDetailSerializer(PublicProductListSerializer):
    images = serializers.SerializerMethodField()

    class Meta(PublicProductListSerializer.Meta):
        fields = PublicProductListSerializer.Meta.fields + [
            "full_description",
            "images",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(PublicProductImageSerializer(many=True))
    def get_images(self, obj) -> list[dict]:
        images = obj.images.order_by("sort_order", "created_at")
        return PublicProductImageSerializer(images, many=True).data


class SellerProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "product_type",
            "base_price",
            "currency",
            "status",
            "category",
            "created_at",
            "updated_at",
        ]


class SellerProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.filter(is_active=True),
        write_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "full_description",
            "product_type",
            "base_price",
            "currency",
            "status",
            "moderation_note",
            "category",
            "category_id",
            "published_at",
            "hidden_at",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "moderation_note",
            "published_at",
            "hidden_at",
            "archived_at",
            "created_at",
            "updated_at",
        ]


class SellerProductCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.filter(is_active=True),
    )

    class Meta:
        model = Product
        fields = [
            "title",
            "slug",
            "short_description",
            "full_description",
            "product_type",
            "base_price",
            "currency",
            "category_id",
        ]


class SellerProductUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "title",
            "slug",
            "short_description",
            "full_description",
            "product_type",
            "base_price",
            "currency",
            "category_id",
        ]
