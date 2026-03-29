from django.contrib import admin

from apps.complaints.models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "submitted_by", "status", "reason", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "product__title",
        "submitted_by__email",
        "submitted_by__username",
        "reason",
    )
