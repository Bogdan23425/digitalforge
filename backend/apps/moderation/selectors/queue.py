from django.db.models import QuerySet

from apps.catalog.models import Product
from apps.common.choices import ProductStatus


def get_pending_review_products() -> QuerySet[Product]:
    return (
        Product.objects.filter(status=ProductStatus.PENDING_REVIEW, is_deleted=False)
        .select_related("seller", "category")
        .order_by("-updated_at")
    )
