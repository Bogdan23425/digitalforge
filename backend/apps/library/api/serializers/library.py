from rest_framework import serializers

from apps.common.choices import FileScanStatus
from apps.library.models import PurchaseAccess


class PurchaseAccessSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    title = serializers.CharField(source="product.title", read_only=True)
    order_id = serializers.UUIDField(source="order_item.order.id", read_only=True)
    order_number = serializers.CharField(
        source="order_item.order.order_number", read_only=True
    )
    has_downloadable_file = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseAccess
        fields = [
            "id",
            "product_id",
            "title",
            "order_id",
            "order_number",
            "is_active",
            "has_downloadable_file",
            "created_at",
        ]

    def get_has_downloadable_file(self, obj):
        current_file = (
            obj.product.files.filter(is_current=True).order_by("-created_at").first()
        )
        return (
            current_file is not None
            and current_file.scan_status == FileScanStatus.CLEAN
        )


class DownloadAuthorizationSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    title = serializers.CharField()
    file_name = serializers.CharField()
    mime_type = serializers.CharField()
    file_size = serializers.IntegerField()
    expires_in = serializers.IntegerField()
    download_url = serializers.URLField()
