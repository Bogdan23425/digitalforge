from apps.common.choices import FileScanStatus


def get_current_downloadable_file(*, purchase_access):
    product_file = (
        purchase_access.product.files.filter(is_current=True)
        .order_by("-created_at")
        .first()
    )
    if product_file is None:
        raise ValueError("No current file is available for this product.")
    if product_file.scan_status != FileScanStatus.CLEAN:
        raise ValueError("The current file is not ready for download yet.")
    return product_file
