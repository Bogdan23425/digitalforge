from django.urls import path

from apps.payments.api.views.payments import (
    PaymentDetailView,
    PaymentListView,
    PaymentSimulateFailureView,
    PaymentSimulatePartialRefundView,
    PaymentSimulateRefundView,
    PaymentSimulateSuccessView,
    PaymentWebhookView,
    PaymentsHealthView,
    StripeWebhookView,
)

urlpatterns = [
    path("health/", PaymentsHealthView.as_view(), name="payments-health"),
    path("webhooks/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<uuid:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path(
        "<uuid:pk>/simulate-success/",
        PaymentSimulateSuccessView.as_view(),
        name="payment-simulate-success",
    ),
    path(
        "<uuid:pk>/simulate-failure/",
        PaymentSimulateFailureView.as_view(),
        name="payment-simulate-failure",
    ),
    path(
        "<uuid:pk>/simulate-partial-refund/",
        PaymentSimulatePartialRefundView.as_view(),
        name="payment-simulate-partial-refund",
    ),
    path(
        "<uuid:pk>/simulate-refund/",
        PaymentSimulateRefundView.as_view(),
        name="payment-simulate-refund",
    ),
]
