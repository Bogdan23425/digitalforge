from django.conf import settings
from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class ModerationAction(UUIDPrimaryKeyModel, TimestampedModel):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="moderation_actions",
    )
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="moderation_actions",
    )
    from_status = models.CharField(max_length=32)
    to_status = models.CharField(max_length=32)
    reason = models.TextField(blank=True)
