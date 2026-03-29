from django.test import override_settings
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.test import APITestCase

from apps.accounts.api.views.auth import (
    LoginView,
    RegisterView,
    ResendVerificationCodeView,
    VerifyEmailView,
)
from apps.accounts.models import User
from apps.orders.api.views.orders import CartItemListCreateView, CheckoutView
from apps.payments.api.views.payments import PaymentWebhookView, StripeWebhookView


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend",
        ],
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
            "rest_framework.throttling.ScopedRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "anon": "1000/hour",
            "user": "3000/hour",
            "auth_register": "1/minute",
            "auth_login": "1/minute",
            "auth_verify_email": "1/minute",
            "auth_resend_verification": "1/minute",
            "cart_write": "1/minute",
            "checkout": "1/minute",
            "complaints_write": "1/minute",
            "notification_write": "1/minute",
            "payment_actions": "1/minute",
            "payment_webhook": "1/minute",
        },
    }
)
class SecurityHardeningTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="hardening-user@example.com",
            username="hardening-user",
            password="StrongPass123",
            email_verified=True,
        )

    def test_risky_endpoints_define_scoped_throttling(self):
        throttled_views = [
            (RegisterView, "auth_register"),
            (LoginView, "auth_login"),
            (VerifyEmailView, "auth_verify_email"),
            (ResendVerificationCodeView, "auth_resend_verification"),
            (CartItemListCreateView, "cart_write"),
            (CheckoutView, "checkout"),
            (PaymentWebhookView, "payment_webhook"),
            (StripeWebhookView, "payment_webhook"),
        ]

        for view_class, expected_scope in throttled_views:
            self.assertEqual(view_class.throttle_scope, expected_scope)
            self.assertEqual(view_class.throttle_classes, [ScopedRateThrottle])

    @override_settings(ENABLE_GENERIC_PAYMENT_WEBHOOK=False)
    def test_generic_payment_webhook_is_disabled_by_default(self):
        response = self.client.post(
            "/api/v1/payments/webhooks/",
            {
                "event_id": "evt_security_disabled",
                "event_type": "payment.succeeded",
                "provider": "stripe",
                "provider_payment_id": "pi_security_disabled",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"],
            "Generic payment webhook is disabled.",
        )
