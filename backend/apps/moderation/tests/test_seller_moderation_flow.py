from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus
from apps.files.models import ProductFile
from apps.moderation.models import ModerationAction


class SellerModerationFlowTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="seller-moderation@example.com",
            username="seller-moderation",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.moderator = User.objects.create_user(
            email="moderator-moderation@example.com",
            username="moderator-moderation",
            password="StrongPass123",
            is_moderator=True,
            email_verified=True,
        )
        self.category = Category.objects.create(
            name="Seller Flow",
            slug="seller-flow",
        )

    def _create_product(self) -> str:
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(
            "/api/v1/seller/products/",
            {
                "title": "Seller Product",
                "slug": "seller-product",
                "short_description": "Short description",
                "full_description": "Full description",
                "product_type": "template",
                "base_price": "49.99",
                "currency": "USD",
                "category_id": str(self.category.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data["id"]

    def _add_cover_image(self, product_id: str) -> None:
        response = self.client.post(
            f"/api/v1/seller/products/{product_id}/images/",
            {
                "image_url": "https://example.com/seller-cover.png",
                "kind": "cover",
                "sort_order": 0,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def _add_product_file(self, product_id: str) -> None:
        response = self.client.post(
            f"/api/v1/seller/products/{product_id}/files/",
            {
                "file_name": "seller-asset.zip",
                "storage_key": f"products/{product_id}/seller-asset.zip",
                "mime_type": "application/zip",
                "file_size": 4096,
                "checksum": "checksum-seller-flow",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submit_requires_cover_image_and_product_file(self):
        product_id = self._create_product()

        missing_cover_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/submit/",
            {},
            format="json",
        )
        self.assertEqual(
            missing_cover_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            missing_cover_response.data["detail"],
            "A cover image is required before review.",
        )

        self._add_cover_image(product_id)
        missing_file_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/submit/",
            {},
            format="json",
        )
        self.assertEqual(
            missing_file_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            missing_file_response.data["detail"],
            "A product file is required before review.",
        )

        self._add_product_file(product_id)
        submit_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/submit/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(submit_response.data["status"], ProductStatus.PENDING_REVIEW)

    def test_request_changes_resubmit_and_approve_flow_records_actions(self):
        product_id = self._create_product()
        self._add_cover_image(product_id)
        self._add_product_file(product_id)

        submit_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/submit/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.moderator)
        queue_response = self.client.get("/api/v1/moderation/products/")
        self.assertEqual(queue_response.status_code, status.HTTP_200_OK)
        self.assertEqual(queue_response.data["count"], 1)
        self.assertEqual(queue_response.data["results"][0]["id"], product_id)

        request_changes_response = self.client.post(
            f"/api/v1/moderation/products/{product_id}/request-changes/",
            {"reason": "Please improve the description."},
            format="json",
        )
        self.assertEqual(request_changes_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            request_changes_response.data["status"], ProductStatus.CHANGES_REQUESTED
        )

        first_action = ModerationAction.objects.get(product_id=product_id)
        self.assertEqual(first_action.from_status, ProductStatus.PENDING_REVIEW)
        self.assertEqual(first_action.to_status, ProductStatus.CHANGES_REQUESTED)
        self.assertEqual(first_action.reason, "Please improve the description.")

        self.client.force_authenticate(user=self.seller)
        patch_response = self.client.patch(
            f"/api/v1/seller/products/{product_id}/",
            {"full_description": "Updated full description after review."},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["status"], ProductStatus.CHANGES_REQUESTED)

        resubmit_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/submit/",
            {},
            format="json",
        )
        self.assertEqual(resubmit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(resubmit_response.data["status"], ProductStatus.PENDING_REVIEW)

        self.client.force_authenticate(user=self.moderator)
        approve_response = self.client.post(
            f"/api/v1/moderation/products/{product_id}/approve/",
            {"reason": "Approved after the update."},
            format="json",
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_response.data["status"], ProductStatus.PUBLISHED)

        actions = ModerationAction.objects.filter(product_id=product_id).order_by(
            "created_at"
        )
        self.assertEqual(actions.count(), 2)
        self.assertEqual(actions[1].from_status, ProductStatus.PENDING_REVIEW)
        self.assertEqual(actions[1].to_status, ProductStatus.PUBLISHED)
        self.assertEqual(actions[1].reason, "Approved after the update.")

    def test_critical_update_on_published_product_returns_it_to_review(self):
        product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Published Product",
            slug="published-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="29.99",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )
        ProductFile.objects.create(
            product=product,
            file_name="published-asset.zip",
            storage_key="products/published/published-asset.zip",
            mime_type="application/zip",
            file_size=1024,
            checksum="checksum-published",
            is_current=True,
        )

        self.client.force_authenticate(user=self.seller)
        response = self.client.patch(
            f"/api/v1/seller/products/{product.id}/",
            {
                "title": "Published Product Updated",
                "base_price": "39.99",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ProductStatus.PENDING_REVIEW)
        self.assertEqual(
            response.data["moderation_note"],
            "Product was sent to re-review after a critical update.",
        )
