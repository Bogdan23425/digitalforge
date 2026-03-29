import re
from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import EmailVerificationStatus, User


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AccountsApiTests(APITestCase):
    def _extract_verification_code(self) -> str:
        self.assertGreater(len(mail.outbox), 0)
        match = re.search(r"(\d{5})", mail.outbox[-1].body)
        self.assertIsNotNone(match)
        return match.group(1)

    @patch(
        "apps.accounts.services.email_verification.send_verification_code_email.delay",
        side_effect=RuntimeError("broker unavailable"),
    )
    def test_register_logs_user_in_and_creates_profile_and_verification(
        self, _mock_delay
    ):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "accounts-register@example.com",
                "username": "accounts-register",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "accounts-register@example.com")
        self.assertFalse(response.data["email_verified"])
        self.assertEqual(response.data["profile"]["locale"], "en")
        self.assertIn("sessionid", self.client.cookies)

        user = User.objects.get(email="accounts-register@example.com")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.email_verifications.count(), 1)
        self.assertEqual(
            user.email_verifications.first().status, EmailVerificationStatus.PENDING
        )

        me_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "accounts-register@example.com")

    def test_login_logout_and_me_flow(self):
        user = User.objects.create_user(
            email="accounts-login@example.com",
            username="accounts-login",
            password="StrongPass123",
        )

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "accounts-login@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data["id"], str(user.id))
        self.assertIn("sessionid", self.client.cookies)

        me_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "accounts-login@example.com")

        logout_response = self.client.post("/api/v1/auth/logout/", {}, format="json")
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

        me_after_logout_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(
            me_after_logout_response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_profile_me_allows_partial_update(self):
        user = User.objects.create_user(
            email="accounts-profile@example.com",
            username="accounts-profile",
            password="StrongPass123",
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            "/api/v1/profile/me/",
            {
                "display_name": "Bogdan",
                "timezone": "Europe/Kyiv",
                "locale": "uk",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], "Bogdan")
        self.assertEqual(response.data["timezone"], "Europe/Kyiv")
        self.assertEqual(response.data["locale"], "uk")

        user.refresh_from_db()
        self.assertEqual(user.profile.display_name, "Bogdan")
        self.assertEqual(user.profile.timezone, "Europe/Kyiv")
        self.assertEqual(user.profile.locale, "uk")

    @patch(
        "apps.accounts.services.email_verification.send_verification_code_email.delay",
        side_effect=RuntimeError("broker unavailable"),
    )
    def test_verify_email_marks_user_verified(self, _mock_delay):
        self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "accounts-verify@example.com",
                "username": "accounts-verify",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
            },
            format="json",
        )
        code = self._extract_verification_code()

        response = self.client.post(
            "/api/v1/auth/verify-email/",
            {"code": code},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["email_verified"])

        user = User.objects.get(email="accounts-verify@example.com")
        verification = user.email_verifications.first()
        self.assertTrue(user.email_verified)
        self.assertEqual(verification.status, EmailVerificationStatus.VERIFIED)
        self.assertIsNotNone(verification.used_at)

    @patch(
        "apps.accounts.services.email_verification.send_verification_code_email.delay",
        side_effect=RuntimeError("broker unavailable"),
    )
    def test_verify_email_rejects_invalid_code_and_tracks_attempts(self, _mock_delay):
        self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "accounts-invalid-code@example.com",
                "username": "accounts-invalid-code",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
            },
            format="json",
        )
        user = User.objects.get(email="accounts-invalid-code@example.com")
        verification = user.email_verifications.first()

        response = self.client.post(
            "/api/v1/auth/verify-email/",
            {"code": "00000"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["detail"], "Invalid verification code.")

        verification.refresh_from_db()
        self.assertEqual(verification.attempts_count, 1)
        self.assertEqual(verification.status, EmailVerificationStatus.PENDING)

    @patch(
        "apps.accounts.services.email_verification.send_verification_code_email.delay",
        side_effect=RuntimeError("broker unavailable"),
    )
    def test_resend_verification_enforces_cooldown_then_reissues_code(
        self, _mock_delay
    ):
        self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "accounts-resend@example.com",
                "username": "accounts-resend",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
            },
            format="json",
        )

        cooldown_response = self.client.post(
            "/api/v1/auth/resend-verification-code/",
            {"email": "accounts-resend@example.com"},
            format="json",
        )
        self.assertEqual(
            cooldown_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            cooldown_response.data["detail"], "Resend cooldown has not passed yet."
        )

        user = User.objects.get(email="accounts-resend@example.com")
        active_verification = user.email_verifications.first()
        active_verification.resend_available_at = timezone.now() - timedelta(seconds=1)
        active_verification.save(update_fields=["resend_available_at"])

        resend_response = self.client.post(
            "/api/v1/auth/resend-verification-code/",
            {"email": "accounts-resend@example.com"},
            format="json",
        )
        self.assertEqual(resend_response.status_code, status.HTTP_204_NO_CONTENT)

        statuses = list(
            user.email_verifications.order_by("-created_at").values_list(
                "status", flat=True
            )
        )
        self.assertEqual(len(statuses), 2)
        self.assertEqual(statuses[0], EmailVerificationStatus.PENDING)
        self.assertEqual(statuses[1], EmailVerificationStatus.CANCELED)
        self.assertEqual(len(mail.outbox), 2)
