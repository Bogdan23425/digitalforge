from django.urls import path

from apps.files.api.views import (
    SellerProductFileDeleteView,
    SellerProductFileListCreateView,
    SellerProductImageDeleteView,
    SellerProductImageListCreateView,
)

urlpatterns = [
    path(
        "<uuid:pk>/images/",
        SellerProductImageListCreateView.as_view(),
        name="seller-product-images",
    ),
    path(
        "<uuid:pk>/images/<uuid:image_id>/",
        SellerProductImageDeleteView.as_view(),
        name="seller-product-image-delete",
    ),
    path(
        "<uuid:pk>/files/",
        SellerProductFileListCreateView.as_view(),
        name="seller-product-files",
    ),
    path(
        "<uuid:pk>/files/<uuid:file_id>/",
        SellerProductFileDeleteView.as_view(),
        name="seller-product-file-delete",
    ),
]
