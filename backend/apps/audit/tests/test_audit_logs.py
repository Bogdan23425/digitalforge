from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus


class AuditLogTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Audit", slug="audit")

    def test_auth_flow_writes_audit_logs(self):
        register_response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "audit-user@example.com",
                "username": "audit-user",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="audit-user@example.com")

        latest_register_log = AuditLog.objects.filter(actor_user=user).latest(
            "created_at"
        )
        self.assertEqual(latest_register_log.action_type, "auth.register")
        self.assertEqual(latest_register_log.entity_type, "user")

        logout_response = self.client.post("/api/v1/auth/logout/", {}, format="json")
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

        action_types = list(
            AuditLog.objects.filter(actor_user=user)
            .order_by("created_at")
            .values_list("action_type", flat=True)
        )
        self.assertIn("auth.register", action_types)
        self.assertIn("auth.logout", action_types)

    def test_checkout_and_moderation_write_audit_logs(self):
        seller = User.objects.create_user(
            email="audit-seller@example.com",
            username="audit-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        buyer = User.objects.create_user(
            email="audit-buyer@example.com",
            username="audit-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        moderator = User.objects.create_user(
            email="audit-moderator@example.com",
            username="audit-moderator",
            password="StrongPass123",
            is_moderator=True,
            email_verified=True,
        )
        product = Product.objects.create(
            seller=seller,
            category=self.category,
            title="Audit Product",
            slug="audit-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="14.00",
            currency="USD",
            status=ProductStatus.PENDING_REVIEW,
        )

        self.client.force_authenticate(user=moderator)
        approve_response = self.client.post(
            f"/api/v1/moderation/products/{product.id}/approve/",
            {"reason": "Approved in audit test."},
            format="json",
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            AuditLog.objects.filter(
                actor_user=moderator,
                action_type="moderation.product_approved",
                entity_type="product",
                entity_id=product.id,
            ).exists()
        )

        self.client.force_authenticate(user=buyer)
        add_to_cart_response = self.client.post(
            "/api/v1/cart/items/",
            {"product_id": str(product.id)},
            format="json",
        )
        self.assertEqual(add_to_cart_response.status_code, status.HTTP_201_CREATED)

        checkout_response = self.client.post(
            "/api/v1/checkout/",
            {"payment_provider": "stripe"},
            format="json",
        )
        self.assertEqual(checkout_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            AuditLog.objects.filter(
                actor_user=buyer,
                action_type="order.checkout_created",
                entity_type="order",
            ).exists()
        )
