from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus
from apps.complaints.models import Complaint


class ComplaintsApiTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="complaint-seller@example.com",
            username="complaint-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.buyer = User.objects.create_user(
            email="complaint-buyer@example.com",
            username="complaint-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        self.moderator = User.objects.create_user(
            email="complaint-moderator@example.com",
            username="complaint-moderator",
            password="StrongPass123",
            is_moderator=True,
            email_verified=True,
        )
        self.category = Category.objects.create(
            name="Complaint Cases",
            slug="complaint-cases",
        )
        self.published_product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Complaint Product",
            slug="complaint-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="12.00",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )
        self.draft_product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Draft Complaint Product",
            slug="draft-complaint-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="12.00",
            currency="USD",
            status=ProductStatus.DRAFT,
        )

    def test_buyer_can_create_and_list_own_complaints(self):
        self.client.force_authenticate(user=self.buyer)
        create_response = self.client.post(
            "/api/v1/complaints/",
            {
                "product_id": str(self.published_product.id),
                "reason": "copyright",
                "details": "Looks copied from another marketplace.",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["status"], "open")
        self.assertEqual(
            create_response.data["product"]["id"], str(self.published_product.id)
        )

        list_response = self.client.get("/api/v1/complaints/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(list_response.data["results"][0]["reason"], "copyright")

    def test_complaint_creation_rejects_own_product_unpublished_and_duplicate(self):
        self.client.force_authenticate(user=self.seller)
        own_product_response = self.client.post(
            "/api/v1/complaints/",
            {
                "product_id": str(self.published_product.id),
                "reason": "test",
            },
            format="json",
        )
        self.assertEqual(
            own_product_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            own_product_response.data["detail"],
            "You cannot submit a complaint for your own product.",
        )

        self.client.force_authenticate(user=self.buyer)
        unpublished_response = self.client.post(
            "/api/v1/complaints/",
            {
                "product_id": str(self.draft_product.id),
                "reason": "test",
            },
            format="json",
        )
        self.assertEqual(
            unpublished_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            unpublished_response.data["detail"],
            "Complaints can only be submitted for published products.",
        )

        first_response = self.client.post(
            "/api/v1/complaints/",
            {
                "product_id": str(self.published_product.id),
                "reason": "spam",
            },
            format="json",
        )
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        duplicate_response = self.client.post(
            "/api/v1/complaints/",
            {
                "product_id": str(self.published_product.id),
                "reason": "spam",
            },
            format="json",
        )
        self.assertEqual(
            duplicate_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            duplicate_response.data["detail"],
            "An active complaint for this product already exists.",
        )

    def test_moderator_can_review_and_update_complaint_status(self):
        complaint = Complaint.objects.create(
            submitted_by=self.buyer,
            product=self.published_product,
            reason="abuse",
            details="Offensive content in assets.",
            status="open",
        )

        self.client.force_authenticate(user=self.moderator)
        moderation_list_response = self.client.get("/api/v1/complaints/moderation/")
        self.assertEqual(moderation_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(moderation_list_response.data["count"], 1)
        self.assertEqual(
            moderation_list_response.data["results"][0]["id"], str(complaint.id)
        )

        update_response = self.client.patch(
            f"/api/v1/complaints/{complaint.id}/status/",
            {"status": "resolved"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["status"], "resolved")

        complaint.refresh_from_db()
        self.assertEqual(complaint.status, "resolved")
