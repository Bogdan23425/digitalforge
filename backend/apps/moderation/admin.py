from django.contrib import admin

from apps.moderation.models import ModerationAction


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "actor_user",
        "from_status",
        "to_status",
        "created_at",
    )
    list_filter = ("from_status", "to_status")
    search_fields = (
        "product__title",
        "product__slug",
        "actor_user__email",
        "actor_user__username",
    )
    autocomplete_fields = ("product", "actor_user")
