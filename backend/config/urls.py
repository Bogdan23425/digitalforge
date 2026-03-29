from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs-swagger",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-docs-redoc",
    ),
    path("api/v1/auth/", include("apps.accounts.api.urls")),
    path("api/v1/profile/", include("apps.accounts.api.profile_urls")),
    path("api/v1/products/", include("apps.catalog.api.urls")),
    path("api/v1/seller/products/", include("apps.catalog.api.seller_urls")),
    path("api/v1/files/", include("apps.files.api.urls")),
    path("api/v1/seller/products/", include("apps.files.api.seller_urls")),
    path("api/v1/moderation/", include("apps.moderation.api.urls")),
    path("api/v1/", include("apps.orders.api.urls")),
    path("api/v1/payments/", include("apps.payments.api.urls")),
    path("api/v1/library/", include("apps.library.api.urls")),
    path("api/v1/complaints/", include("apps.complaints.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
