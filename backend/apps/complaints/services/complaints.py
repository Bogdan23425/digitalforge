from django.db import transaction

from apps.common.choices import ProductStatus
from apps.complaints.models import Complaint

ACTIVE_COMPLAINT_STATUSES = {"open", "in_review"}


@transaction.atomic
def create_complaint(*, submitted_by, product, reason: str, details: str = ""):
    if product.status != ProductStatus.PUBLISHED:
        raise ValueError("Complaints can only be submitted for published products.")
    if product.seller_id == submitted_by.id:
        raise ValueError("You cannot submit a complaint for your own product.")
    if Complaint.objects.filter(
        submitted_by=submitted_by,
        product=product,
        status__in=ACTIVE_COMPLAINT_STATUSES,
    ).exists():
        raise ValueError("An active complaint for this product already exists.")

    return Complaint.objects.create(
        submitted_by=submitted_by,
        product=product,
        reason=reason,
        details=details,
        status="open",
    )


@transaction.atomic
def update_complaint_status(*, complaint: Complaint, status_value: str):
    complaint.status = status_value
    complaint.save(update_fields=["status", "updated_at"])
    return complaint
