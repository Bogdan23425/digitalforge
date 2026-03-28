from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.api.urls")),
    path("api/v1/profile/", include("apps.accounts.api.profile_urls")),
    path("api/v1/products/", include("apps.catalog.api.urls")),
    path("api/v1/files/", include("apps.files.api.urls")),
    path("api/v1/moderation/", include("apps.moderation.api.urls")),
    path("api/v1/", include("apps.orders.api.urls")),
    path("api/v1/payments/", include("apps.payments.api.urls")),
    path("api/v1/library/", include("apps.library.api.urls")),
    path("api/v1/complaints/", include("apps.complaints.api.urls")),
]
