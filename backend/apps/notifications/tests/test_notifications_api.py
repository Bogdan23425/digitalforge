from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus
from apps.notifications.models import Notification
from apps.notifications.services import create_notification


class NotificationsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="notifications-user@example.com",
            username="notifications-user",
            password="StrongPass123",
            email_verified=True,
        )
        self.other_user = User.objects.create_user(
            email="notifications-other@example.com",
            username="notifications-other",
            password="StrongPass123",
            email_verified=True,
        )

    def test_user_can_list_and_mark_notifications_as_read(self):
        first = create_notification(
            user=self.user,
            notification_type="test.one",
            title="First",
            body="First body",
        )
        second = create_notification(
            user=self.user,
            notification_type="test.two",
            title="Second",
            body="Second body",
        )
        create_notification(
            user=self.other_user,
            notification_type="test.other",
            title="Other",
            body="Other body",
        )

        self.client.force_authenticate(user=self.user)
        list_response = self.client.get("/api/v1/notifications/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 2)
        self.assertEqual(len(list_response.data["results"]), 2)

        read_response = self.client.post(
            f"/api/v1/notifications/{first.id}/read/",
            {},
            format="json",
        )
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertTrue(read_response.data["is_read"])

        read_all_response = self.client.post(
            "/api/v1/notifications/read-all/",
            {},
            format="json",
        )
        self.assertEqual(read_all_response.status_code, status.HTTP_200_OK)
        self.assertEqual(read_all_response.data["updated_count"], 1)

        second.refresh_from_db()
        self.assertTrue(second.is_read)

    def test_user_cannot_mark_foreign_notification_as_read(self):
        foreign = create_notification(
            user=self.other_user,
            notification_type="test.foreign",
            title="Foreign",
            body="Foreign body",
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/v1/notifications/{foreign.id}/read/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Notification not found.")


class NotificationIntegrationTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="notifications-seller@example.com",
            username="notifications-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.moderator = User.objects.create_user(
            email="notifications-moderator@example.com",
            username="notifications-moderator",
            password="StrongPass123",
            is_moderator=True,
            email_verified=True,
        )
        self.category = Category.objects.create(
            name="Notification Category",
            slug="notification-category",
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Notification Product",
            slug="notification-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="10.00",
            currency="USD",
            status=ProductStatus.PENDING_REVIEW,
        )

    def test_moderation_action_creates_seller_notification(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(
            f"/api/v1/moderation/products/{self.product.id}/approve/",
            {"reason": "Approved for publishing."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification = Notification.objects.get(user=self.seller)
        self.assertEqual(notification.type, "product.approved")
        self.assertEqual(notification.title, "Product approved")
