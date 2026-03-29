from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import FileScanStatus, ProductStatus
from apps.files.models import ProductFile
from apps.library.models import PurchaseAccess
from apps.library.services.downloads import build_signed_download_token
from apps.orders.models import Order, OrderItem


@override_settings(PRIVATE_STORAGE_BASE_URL="https://downloads.example.com/private")
class LibraryEdgeCaseTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="library-seller@example.com",
            username="library-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.buyer = User.objects.create_user(
            email="library-buyer@example.com",
            username="library-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        self.other_buyer = User.objects.create_user(
            email="library-other-buyer@example.com",
            username="library-other-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        self.category = Category.objects.create(
            name="Library Cases",
            slug="library-cases",
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Library Product",
            slug="library-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="24.99",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            order_number="ORD-LIBRARY-EDGE",
            status="fulfilled",
            subtotal_amount="24.99",
            platform_fee_amount="2.50",
            total_amount="24.99",
            currency="USD",
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            seller=self.seller,
            unit_price="24.99",
            final_price="24.99",
            platform_fee_amount="2.50",
            seller_net_amount="22.49",
        )
        self.purchase_access = PurchaseAccess.objects.create(
            order_item=self.order_item,
            buyer=self.buyer,
            product=self.product,
        )
        self.product_file = ProductFile.objects.create(
            product=self.product,
            file_name="library-asset.zip",
            storage_key="products/library/library-asset.zip",
            mime_type="application/zip",
            file_size=4096,
            checksum="checksum-library",
            is_current=True,
            scan_status=FileScanStatus.CLEAN,
        )

    def test_secure_download_rejects_invalid_and_foreign_tokens(self):
        self.client.force_authenticate(user=self.buyer)
        invalid_response = self.client.get("/api/v1/library/downloads/not-a-token/")
        self.assertEqual(invalid_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            invalid_response.data["detail"], "Download token is invalid or expired."
        )

        foreign_token = build_signed_download_token(
            user_id=self.other_buyer.id,
            product_id=self.product.id,
            file_id=self.product_file.id,
        )
        foreign_response = self.client.get(
            f"/api/v1/library/downloads/{foreign_token}/"
        )
        self.assertEqual(foreign_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            foreign_response.data["detail"],
            "Download token does not belong to the current user.",
        )

    def test_download_authorization_requires_clean_current_file(self):
        self.client.force_authenticate(user=self.buyer)
        self.product_file.scan_status = FileScanStatus.PENDING
        self.product_file.save(update_fields=["scan_status"])

        response = self.client.get(f"/api/v1/library/{self.product.id}/download/")

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.data["detail"], "The current file is not ready for download yet."
        )

    def test_secure_download_rejects_token_for_old_file_after_file_rotation(self):
        self.client.force_authenticate(user=self.buyer)
        stale_token = build_signed_download_token(
            user_id=self.buyer.id,
            product_id=self.product.id,
            file_id=self.product_file.id,
        )
        self.product_file.is_current = False
        self.product_file.save(update_fields=["is_current"])
        ProductFile.objects.create(
            product=self.product,
            file_name="library-asset-v2.zip",
            storage_key="products/library/library-asset-v2.zip",
            mime_type="application/zip",
            file_size=8192,
            checksum="checksum-library-v2",
            is_current=True,
            scan_status=FileScanStatus.CLEAN,
        )

        response = self.client.get(f"/api/v1/library/downloads/{stale_token}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "Download token does not match the current product file.",
        )
