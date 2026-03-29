from django.urls import path

from apps.moderation.api.views import (
    ApproveProductView,
    ModerationHealthView,
    ModerationQueueView,
    RejectProductView,
    RequestChangesView,
)

urlpatterns = [
    path("health/", ModerationHealthView.as_view(), name="moderation-health"),
    path("products/", ModerationQueueView.as_view(), name="moderation-queue"),
    path(
        "products/<uuid:pk>/approve/",
        ApproveProductView.as_view(),
        name="moderation-approve",
    ),
    path(
        "products/<uuid:pk>/request-changes/",
        RequestChangesView.as_view(),
        name="moderation-request-changes",
    ),
    path(
        "products/<uuid:pk>/reject/",
        RejectProductView.as_view(),
        name="moderation-reject",
    ),
]
