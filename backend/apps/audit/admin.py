from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "action_type",
        "entity_type",
        "entity_id",
        "actor_user",
        "created_at",
    )
    list_filter = ("action_type", "entity_type", "created_at")
    search_fields = (
        "action_type",
        "entity_type",
        "actor_user__email",
        "actor_user__username",
    )
