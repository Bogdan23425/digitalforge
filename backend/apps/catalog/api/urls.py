from django.urls import path

from apps.catalog.api.views.products import (
    CatalogHealthView,
    CategoryListView,
    PublicProductDetailView,
    PublicProductListView,
)

urlpatterns = [
    path("health/", CatalogHealthView.as_view(), name="catalog-health"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("", PublicProductListView.as_view(), name="public-product-list"),
    path(
        "<slug:slug>/", PublicProductDetailView.as_view(), name="public-product-detail"
    ),
]
