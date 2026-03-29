from django.contrib import admin

from apps.files.models import ProductFile, ProductImage


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "kind", "sort_order", "created_at")
    list_filter = ("kind",)
    search_fields = ("product__title", "product__slug", "image_url")
    autocomplete_fields = ("product",)


@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "file_name",
        "is_current",
        "scan_status",
        "file_size",
        "created_at",
    )
    list_filter = ("is_current", "scan_status", "mime_type")
    search_fields = ("product__title", "product__slug", "file_name", "storage_key")
    autocomplete_fields = ("product",)
