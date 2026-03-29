from django.urls import path

from apps.notifications.api.views import (
    NotificationListView,
    NotificationReadAllView,
    NotificationReadView,
    NotificationsHealthView,
)

urlpatterns = [
    path("health/", NotificationsHealthView.as_view(), name="notifications-health"),
    path("", NotificationListView.as_view(), name="notifications-list"),
    path("<uuid:pk>/read/", NotificationReadView.as_view(), name="notifications-read"),
    path("read-all/", NotificationReadAllView.as_view(), name="notifications-read-all"),
]
