from django.db import models

from apps.common.db.models import TimestampedModel, UUIDPrimaryKeyModel


class Category(UUIDPrimaryKeyModel, TimestampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    is_active = models.BooleanField(default=True)
