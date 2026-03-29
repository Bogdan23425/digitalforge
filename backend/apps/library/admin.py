from django.contrib import admin

from apps.library.models import PurchaseAccess


@admin.register(PurchaseAccess)
class PurchaseAccessAdmin(admin.ModelAdmin):
    list_display = ("buyer", "product", "is_active", "revoked_at", "created_at")
    list_filter = ("is_active",)
    search_fields = (
        "buyer__email",
        "buyer__username",
        "product__title",
        "product__slug",
    )
    autocomplete_fields = ("buyer", "product", "order_item")
