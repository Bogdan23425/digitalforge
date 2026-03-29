from rest_framework import serializers

from apps.complaints.models import Complaint
from apps.catalog.models import Product


class ComplaintProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "slug"]


class ComplaintUserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)


class ComplaintSerializer(serializers.ModelSerializer):
    product = ComplaintProductSerializer(read_only=True)
    submitted_by = ComplaintUserSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "id",
            "status",
            "reason",
            "details",
            "product",
            "submitted_by",
            "created_at",
            "updated_at",
        ]


class ComplaintCreateSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.filter(is_deleted=False),
    )
    reason = serializers.CharField(max_length=100)
    details = serializers.CharField(required=False, allow_blank=True)


class ComplaintStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["open", "in_review", "resolved", "dismissed"]
    )
