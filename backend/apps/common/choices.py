from django.db import models


class ProductStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_REVIEW = "pending_review", "Pending review"
    CHANGES_REQUESTED = "changes_requested", "Changes requested"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"
    HIDDEN = "hidden", "Hidden"
    ARCHIVED = "archived", "Archived"


class OrderStatus(models.TextChoices):
    CREATED = "created", "Created"
    PENDING_PAYMENT = "pending_payment", "Pending payment"
    PAID = "paid", "Paid"
    FULFILLED = "fulfilled", "Fulfilled"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"


class PaymentStatus(models.TextChoices):
    INITIATED = "initiated", "Initiated"
    PROCESSING = "processing", "Processing"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"
    DISPUTED = "disputed", "Disputed"
