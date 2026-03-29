from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus
from apps.notifications.models import Notification
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment


class ApiPermissionSmokeTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="permissions-seller@example.com",
            username="permissions-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.other_seller = User.objects.create_user(
            email="permissions-other-seller@example.com",
            username="permissions-other-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.buyer = User.objects.create_user(
            email="permissions-buyer@example.com",
            username="permissions-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        self.other_buyer = User.objects.create_user(
            email="permissions-other-buyer@example.com",
            username="permissions-other-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        self.moderator = User.objects.create_user(
            email="permissions-moderator@example.com",
            username="permissions-moderator",
            password="StrongPass123",
            is_moderator=True,
            email_verified=True,
        )
        self.category = Category.objects.create(
            name="Permission Cases",
            slug="permission-cases",
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Permission Product",
            slug="permission-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="19.99",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )
        self.other_product = Product.objects.create(
            seller=self.other_seller,
            category=self.category,
            title="Other Seller Product",
            slug="other-seller-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="29.99",
            currency="USD",
            status=ProductStatus.DRAFT,
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            order_number="ORD-PERMISSIONS-TEST",
            status="pending_payment",
            subtotal_amount="19.99",
            platform_fee_amount="2.00",
            total_amount="19.99",
            currency="USD",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            seller=self.seller,
            unit_price="19.99",
            final_price="19.99",
            platform_fee_amount="2.00",
            seller_net_amount="17.99",
        )
        self.payment = Payment.objects.create(
            order=self.order,
            provider="stripe",
            amount="19.99",
            currency="USD",
        )
        self.notification = Notification.objects.create(
            user=self.buyer,
            type="test.permission",
            title="Permission Notification",
            body="Body",
        )

    def test_anonymous_user_cannot_access_protected_endpoints(self):
        protected_endpoints = [
            "/api/v1/auth/me/",
            "/api/v1/profile/me/",
            "/api/v1/orders/",
            "/api/v1/payments/",
            "/api/v1/library/",
            "/api/v1/notifications/",
            "/api/v1/complaints/",
        ]

        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_seller_and_non_moderator_users_cannot_access_privileged_endpoints(
        self,
    ):
        self.client.force_authenticate(user=self.buyer)

        seller_response = self.client.post(
            "/api/v1/seller/products/",
            {
                "title": "Should Fail",
                "slug": "should-fail",
                "short_description": "Short",
                "full_description": "Full",
                "product_type": "template",
                "base_price": "10.00",
                "currency": "USD",
                "category_id": str(self.category.id),
            },
            format="json",
        )
        self.assertEqual(seller_response.status_code, status.HTTP_403_FORBIDDEN)

        moderation_response = self.client.get("/api/v1/moderation/products/")
        self.assertEqual(moderation_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seller_cannot_access_another_seller_product_resources(self):
        self.client.force_authenticate(user=self.seller)

        detail_response = self.client.get(
            f"/api/v1/seller/products/{self.other_product.id}/"
        )
        self.assertEqual(detail_response.status_code, status.HTTP_403_FORBIDDEN)

        patch_response = self.client.patch(
            f"/api/v1/seller/products/{self.other_product.id}/",
            {"title": "Hijack"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        file_response = self.client.post(
            f"/api/v1/seller/products/{self.other_product.id}/files/",
            {
                "file_name": "stolen.zip",
                "storage_key": "products/stolen.zip",
                "mime_type": "application/zip",
                "file_size": 123,
                "checksum": "checksum",
            },
            format="json",
        )
        self.assertEqual(file_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_access_foreign_order_payment_or_notification(self):
        self.client.force_authenticate(user=self.other_buyer)

        order_response = self.client.get(f"/api/v1/orders/{self.order.id}/")
        self.assertEqual(order_response.status_code, status.HTTP_404_NOT_FOUND)

        payment_response = self.client.get(f"/api/v1/payments/{self.payment.id}/")
        self.assertEqual(payment_response.status_code, status.HTTP_404_NOT_FOUND)

        notification_response = self.client.post(
            f"/api/v1/notifications/{self.notification.id}/read/",
            {},
            format="json",
        )
        self.assertEqual(notification_response.status_code, status.HTTP_404_NOT_FOUND)
