from django.conf import settings
from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Profile(UUIDPrimaryKeyModel, TimestampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=2, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    locale = models.CharField(max_length=10, blank=True, default="en")
