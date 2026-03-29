from rest_framework import serializers

from apps.files.models import ProductFile, ProductImage


class ProductImageCreateSerializer(serializers.Serializer):
    image_url = serializers.URLField()
    kind = serializers.ChoiceField(choices=["cover", "gallery"], default="gallery")
    sort_order = serializers.IntegerField(required=False, default=0, min_value=0)


class ProductFileCreateSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    storage_key = serializers.CharField(max_length=500)
    mime_type = serializers.CharField(max_length=100)
    file_size = serializers.IntegerField(min_value=1)
    checksum = serializers.CharField(max_length=128, required=False, allow_blank=True)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "kind", "sort_order", "created_at"]


class ProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFile
        fields = [
            "id",
            "file_name",
            "storage_key",
            "mime_type",
            "file_size",
            "checksum",
            "is_current",
            "scan_status",
            "created_at",
        ]
