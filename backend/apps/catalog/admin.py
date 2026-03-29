from django.contrib import admin

from apps.catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "seller",
        "category",
        "status",
        "base_price",
        "currency",
        "published_at",
        "created_at",
    )
    list_filter = ("status", "currency", "category")
    search_fields = ("title", "slug", "seller__email", "seller__username")
    autocomplete_fields = ("seller", "category")
