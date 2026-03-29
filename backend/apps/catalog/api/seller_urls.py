from django.urls import path

from apps.catalog.api.views.products import (
    SellerProductDetailView,
    SellerProductListCreateView,
    SellerProductSubmitView,
)

urlpatterns = [
    path("", SellerProductListCreateView.as_view(), name="seller-product-list-create"),
    path("<uuid:pk>/", SellerProductDetailView.as_view(), name="seller-product-detail"),
    path(
        "<uuid:pk>/submit/",
        SellerProductSubmitView.as_view(),
        name="seller-product-submit",
    ),
]
