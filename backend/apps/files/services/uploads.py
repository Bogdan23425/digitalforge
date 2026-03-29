from django.db import transaction

from apps.catalog.models import Product
from apps.files.models import ProductFile, ProductImage


@transaction.atomic
def add_product_image(
    *,
    product: Product,
    image_url: str,
    kind: str = "gallery",
    sort_order: int = 0,
) -> ProductImage:
    if kind == "cover":
        product.images.filter(kind="cover").update(kind="gallery")
    return ProductImage.objects.create(
        product=product,
        image_url=image_url,
        kind=kind,
        sort_order=sort_order,
    )


@transaction.atomic
def add_product_file(
    *,
    product: Product,
    file_name: str,
    storage_key: str,
    mime_type: str,
    file_size: int,
    checksum: str = "",
) -> ProductFile:
    product.files.filter(is_current=True).update(is_current=False)
    return ProductFile.objects.create(
        product=product,
        file_name=file_name,
        storage_key=storage_key,
        mime_type=mime_type,
        file_size=file_size,
        checksum=checksum,
        is_current=True,
    )
