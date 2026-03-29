from django.urls import path
from apps.complaints.api.views.complaints import (
    ComplaintListCreateView,
    ComplaintStatusUpdateView,
    ComplaintsHealthView,
    ModerationComplaintListView,
)


urlpatterns = [
    path("health/", ComplaintsHealthView.as_view(), name="complaints-health"),
    path("", ComplaintListCreateView.as_view(), name="complaints-list-create"),
    path(
        "moderation/",
        ModerationComplaintListView.as_view(),
        name="complaints-moderation-list",
    ),
    path(
        "<uuid:pk>/status/",
        ComplaintStatusUpdateView.as_view(),
        name="complaints-status-update",
    ),
]
