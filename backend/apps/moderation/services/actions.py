from django.db import transaction
from django.utils import timezone

from apps.audit.services import write_audit_log
from apps.catalog.models import Product
from apps.common.choices import ProductStatus
from apps.moderation.models import ModerationAction
from apps.notifications.services import create_notification


def _record_action(
    *, product: Product, actor_user, from_status: str, to_status: str, reason: str = ""
):
    return ModerationAction.objects.create(
        product=product,
        actor_user=actor_user,
        from_status=from_status,
        to_status=to_status,
        reason=reason,
    )


@transaction.atomic
def approve_product(*, product: Product, actor_user, reason: str = "") -> Product:
    if product.status != ProductStatus.PENDING_REVIEW:
        raise ValueError("Only products in pending_review can be approved.")

    from_status = product.status
    product.status = ProductStatus.PUBLISHED
    product.moderation_note = reason
    product.published_at = timezone.now()
    product.hidden_at = None
    product.save(
        update_fields=[
            "status",
            "moderation_note",
            "published_at",
            "hidden_at",
            "updated_at",
        ]
    )
    _record_action(
        product=product,
        actor_user=actor_user,
        from_status=from_status,
        to_status=product.status,
        reason=reason,
    )
    create_notification(
        user=product.seller,
        notification_type="product.approved",
        title="Product approved",
        body=f'Your product "{product.title}" was approved and published.',
    )
    write_audit_log(
        actor_user=actor_user,
        action_type="moderation.product_approved",
        entity_type="product",
        entity_id=product.id,
        metadata={"reason": reason},
    )
    return product


@transaction.atomic
def request_changes(*, product: Product, actor_user, reason: str) -> Product:
    if product.status != ProductStatus.PENDING_REVIEW:
        raise ValueError("Only products in pending_review can receive change requests.")
    if not reason.strip():
        raise ValueError("Reason is required when requesting changes.")

    from_status = product.status
    product.status = ProductStatus.CHANGES_REQUESTED
    product.moderation_note = reason
    product.save(update_fields=["status", "moderation_note", "updated_at"])
    _record_action(
        product=product,
        actor_user=actor_user,
        from_status=from_status,
        to_status=product.status,
        reason=reason,
    )
    create_notification(
        user=product.seller,
        notification_type="product.changes_requested",
        title="Product needs changes",
        body=f'Changes were requested for "{product.title}". Reason: {reason}',
    )
    write_audit_log(
        actor_user=actor_user,
        action_type="moderation.product_changes_requested",
        entity_type="product",
        entity_id=product.id,
        metadata={"reason": reason},
    )
    return product


@transaction.atomic
def reject_product(*, product: Product, actor_user, reason: str) -> Product:
    if product.status != ProductStatus.PENDING_REVIEW:
        raise ValueError("Only products in pending_review can be rejected.")
    if not reason.strip():
        raise ValueError("Reason is required when rejecting a product.")

    from_status = product.status
    product.status = ProductStatus.REJECTED
    product.moderation_note = reason
    product.published_at = None
    product.save(
        update_fields=["status", "moderation_note", "published_at", "updated_at"]
    )
    _record_action(
        product=product,
        actor_user=actor_user,
        from_status=from_status,
        to_status=product.status,
        reason=reason,
    )
    create_notification(
        user=product.seller,
        notification_type="product.rejected",
        title="Product rejected",
        body=f'Your product "{product.title}" was rejected. Reason: {reason}',
    )
    write_audit_log(
        actor_user=actor_user,
        action_type="moderation.product_rejected",
        entity_type="product",
        entity_id=product.id,
        metadata={"reason": reason},
    )
    return product
