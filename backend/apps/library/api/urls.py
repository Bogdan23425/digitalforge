from django.urls import path

from apps.library.api.views.library import (
    LibraryDownloadAuthorizationView,
    LibraryHealthView,
    LibraryListView,
    LibrarySecureDownloadView,
)

urlpatterns = [
    path("health/", LibraryHealthView.as_view(), name="library-health"),
    path("", LibraryListView.as_view(), name="library-list"),
    path(
        "downloads/<str:token>/",
        LibrarySecureDownloadView.as_view(),
        name="library-secure-download",
    ),
    path(
        "<uuid:product_id>/download/",
        LibraryDownloadAuthorizationView.as_view(),
        name="library-download-authorization",
    ),
]
