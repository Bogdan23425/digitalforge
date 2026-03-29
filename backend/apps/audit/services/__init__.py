from django.db import transaction

from apps.audit.models import AuditLog


@transaction.atomic
def write_audit_log(
    *,
    action_type: str,
    entity_type: str,
    actor_user=None,
    entity_id=None,
    metadata: dict | None = None,
):
    return AuditLog.objects.create(
        actor_user=actor_user,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )


__all__ = ["write_audit_log"]
