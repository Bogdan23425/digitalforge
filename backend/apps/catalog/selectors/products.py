from django.db.models import QuerySet

from apps.catalog.models import Product
from apps.common.choices import ProductStatus


def get_seller_products(*, seller_id) -> QuerySet[Product]:
    return Product.objects.filter(seller_id=seller_id, is_deleted=False).select_related(
        "category"
    )


def get_public_products() -> QuerySet[Product]:
    return (
        Product.objects.filter(
            status=ProductStatus.PUBLISHED,
            is_deleted=False,
        )
        .select_related("category", "seller")
        .prefetch_related("images", "files")
        .order_by("-published_at", "-created_at")
    )


def get_public_product_by_slug(*, slug: str) -> Product | None:
    return get_public_products().filter(slug=slug).first()
