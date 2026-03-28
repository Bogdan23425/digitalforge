from django.conf import settings
from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Notification(UUIDPrimaryKeyModel, TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
