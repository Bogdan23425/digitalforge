from django.urls import path

from apps.accounts.api.views import ProfileMeView

urlpatterns = [
    path("me/", ProfileMeView.as_view(), name="profile-me"),
]
