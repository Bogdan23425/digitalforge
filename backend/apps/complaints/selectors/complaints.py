from apps.complaints.models import Complaint


def get_user_complaints(*, user):
    return (
        Complaint.objects.select_related("product", "submitted_by")
        .filter(submitted_by=user)
        .order_by("-created_at")
    )


def get_moderation_complaints():
    return Complaint.objects.select_related("product", "submitted_by").order_by(
        "-created_at"
    )
