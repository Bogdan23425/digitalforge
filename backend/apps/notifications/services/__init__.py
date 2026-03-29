from django.db import transaction

from apps.notifications.models import Notification


@transaction.atomic
def create_notification(*, user, notification_type: str, title: str, body: str):
    return Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        body=body,
    )


@transaction.atomic
def mark_notification_read(*, notification: Notification):
    if notification.is_read:
        return notification
    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])
    return notification


@transaction.atomic
def mark_all_notifications_read(*, user) -> int:
    return Notification.objects.filter(user=user, is_read=False).update(is_read=True)


__all__ = [
    "create_notification",
    "mark_notification_read",
    "mark_all_notifications_read",
]
