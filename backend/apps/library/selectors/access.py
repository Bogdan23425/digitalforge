from apps.library.models import PurchaseAccess


def get_user_purchase_accesses(*, user):
    return (
        PurchaseAccess.objects.select_related("product", "order_item__order")
        .prefetch_related("product__files")
        .filter(buyer=user, is_active=True)
        .order_by("-created_at")
    )


def get_user_purchase_access_for_product(*, user, product_id):
    return (
        PurchaseAccess.objects.select_related("product", "order_item__order")
        .prefetch_related("product__files")
        .filter(buyer=user, product_id=product_id, is_active=True)
        .first()
    )
