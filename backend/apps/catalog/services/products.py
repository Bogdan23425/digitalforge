from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Product
from apps.common.choices import ProductStatus
from apps.common.choices import FileScanStatus


@transaction.atomic
def create_product(*, seller, **data) -> Product:
    return Product.objects.create(seller=seller, **data)


@transaction.atomic
def update_product(*, product: Product, **data) -> Product:
    status_before = product.status
    critical_fields = {
        "title",
        "short_description",
        "full_description",
        "category",
        "base_price",
        "currency",
        "product_type",
    }

    for field, value in data.items():
        setattr(product, field, value)

    if status_before == ProductStatus.PUBLISHED and critical_fields.intersection(
        data.keys()
    ):
        product.status = ProductStatus.PENDING_REVIEW
        product.moderation_note = (
            "Product was sent to re-review after a critical update."
        )
        product.published_at = None

    product.save()
    return product


@transaction.atomic
def submit_product_for_review(*, product: Product) -> Product:
    if product.status not in {
        ProductStatus.DRAFT,
        ProductStatus.CHANGES_REQUESTED,
        ProductStatus.REJECTED,
    }:
        raise ValueError(
            "Product cannot be submitted for review from the current status."
        )

    required_fields = [
        product.title,
        product.slug,
        product.short_description,
        product.full_description,
        product.product_type,
    ]
    if not all(required_fields):
        raise ValueError("Product is missing required fields.")
    if not product.images.filter(kind="cover").exists():
        raise ValueError("A cover image is required before review.")
    if not product.files.filter(is_current=True).exists():
        raise ValueError("A product file is required before review.")
    if not product.files.filter(
        is_current=True, scan_status__in=[FileScanStatus.PENDING, FileScanStatus.CLEAN]
    ).exists():
        raise ValueError("Current product file must be pending scan or clean.")

    product.status = ProductStatus.PENDING_REVIEW
    product.moderation_note = ""
    product.save(update_fields=["status", "moderation_note", "updated_at"])
    return product


@transaction.atomic
def archive_product(*, product: Product) -> Product:
    product.status = ProductStatus.ARCHIVED
    product.archived_at = timezone.now()
    product.save(update_fields=["status", "archived_at", "updated_at"])
    return product
