import hashlib
import hmac
import json
import time

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import FileScanStatus, ProductStatus
from apps.files.models import ProductFile
from apps.library.models import PurchaseAccess
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment, PaymentWebhookEvent


@override_settings(PRIVATE_STORAGE_BASE_URL="https://downloads.example.com/private")
class CheckoutWebhookLibraryFlowTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="seller-e2e@example.com",
            username="seller-e2e",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.moderator = User.objects.create_user(
            email="moderator-e2e@example.com",
            username="moderator-e2e",
            password="StrongPass123",
            is_moderator=True,
            email_verified=True,
        )
        self.buyer = User.objects.create_user(
            email="buyer-e2e@example.com",
            username="buyer-e2e",
            password="StrongPass123",
            email_verified=True,
        )
        self.category = Category.objects.create(name="E2E", slug="e2e")

    def test_main_flow_from_seller_to_library_access(self):
        self.client.force_authenticate(user=self.seller)
        create_response = self.client.post(
            "/api/v1/seller/products/",
            {
                "title": "E2E Product",
                "slug": "e2e-product",
                "short_description": "Short description",
                "full_description": "Full description",
                "product_type": "template",
                "base_price": "29.99",
                "currency": "USD",
                "category_id": str(self.category.id),
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        product_id = create_response.data["id"]

        image_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/images/",
            {
                "image_url": "https://example.com/cover.png",
                "kind": "cover",
                "sort_order": 0,
            },
            format="json",
        )
        self.assertEqual(image_response.status_code, status.HTTP_201_CREATED)

        file_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/files/",
            {
                "file_name": "asset.zip",
                "storage_key": "products/e2e/asset.zip",
                "mime_type": "application/zip",
                "file_size": 2048,
                "checksum": "checksum-e2e",
            },
            format="json",
        )
        self.assertEqual(file_response.status_code, status.HTTP_201_CREATED)
        ProductFile.objects.filter(product_id=product_id, is_current=True).update(
            scan_status=FileScanStatus.CLEAN
        )

        submit_response = self.client.post(
            f"/api/v1/seller/products/{product_id}/submit/",
            {},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(submit_response.data["status"], ProductStatus.PENDING_REVIEW)

        self.client.force_authenticate(user=self.moderator)
        approve_response = self.client.post(
            f"/api/v1/moderation/products/{product_id}/approve/",
            {"reason": "Looks good."},
            format="json",
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_response.data["status"], ProductStatus.PUBLISHED)

        self.client.force_authenticate(user=self.buyer)
        public_list_response = self.client.get("/api/v1/products/")
        self.assertEqual(public_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(public_list_response.data["count"], 1)

        add_to_cart_response = self.client.post(
            "/api/v1/cart/items/",
            {"product_id": product_id},
            format="json",
        )
        self.assertEqual(add_to_cart_response.status_code, status.HTTP_201_CREATED)

        checkout_response = self.client.post(
            "/api/v1/checkout/",
            {"payment_provider": "stripe"},
            format="json",
        )
        self.assertEqual(checkout_response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=checkout_response.data["id"])
        payment = Payment.objects.get(order=order)

        processing_webhook_response = self.client.post(
            "/api/v1/payments/webhooks/",
            {
                "provider": "stripe",
                "event_id": "evt_e2e_processing",
                "event_type": "payment.processing",
                "payment_id": str(payment.id),
                "provider_payment_id": "pi_e2e",
                "payload": {"step": "processing"},
            },
            format="json",
        )
        self.assertEqual(processing_webhook_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            processing_webhook_response.data["payment"]["status"], "processing"
        )

        success_webhook_response = self.client.post(
            "/api/v1/payments/webhooks/",
            {
                "provider": "stripe",
                "event_id": "evt_e2e_success",
                "event_type": "payment.succeeded",
                "provider_payment_id": "pi_e2e",
                "payload": {"step": "success"},
            },
            format="json",
        )
        self.assertEqual(success_webhook_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            success_webhook_response.data["payment"]["status"], "succeeded"
        )
        self.assertEqual(
            success_webhook_response.data["payment"]["order_status"], "fulfilled"
        )

        repeated_webhook_response = self.client.post(
            "/api/v1/payments/webhooks/",
            {
                "provider": "stripe",
                "event_id": "evt_e2e_success",
                "event_type": "payment.succeeded",
                "provider_payment_id": "pi_e2e",
                "payload": {"step": "success-repeat"},
            },
            format="json",
        )
        self.assertEqual(repeated_webhook_response.status_code, status.HTTP_200_OK)
        self.assertFalse(repeated_webhook_response.data["created"])
        self.assertFalse(repeated_webhook_response.data["processed"])

        library_response = self.client.get("/api/v1/library/")
        self.assertEqual(library_response.status_code, status.HTTP_200_OK)
        self.assertEqual(library_response.data["count"], 1)
        self.assertTrue(library_response.data["results"][0]["has_downloadable_file"])

        download_response = self.client.get(
            f"/api/v1/library/{product_id}/download/",
        )
        self.assertEqual(download_response.status_code, status.HTTP_200_OK)
        self.assertEqual(download_response.data["file_name"], "asset.zip")
        self.assertIn(
            "/api/v1/library/downloads/", download_response.data["download_url"]
        )

        secure_download_response = self.client.get(
            download_response.data["download_url"]
        )
        self.assertEqual(secure_download_response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            secure_download_response["Location"],
            "https://downloads.example.com/private/products/e2e/asset.zip",
        )

        partial_refund_response = self.client.post(
            f"/api/v1/payments/{payment.id}/simulate-partial-refund/",
            {"refunded_amount": "10.00"},
            format="json",
        )
        self.assertEqual(partial_refund_response.status_code, status.HTTP_200_OK)
        self.assertEqual(partial_refund_response.data["status"], "partially_refunded")
        self.assertEqual(
            partial_refund_response.data["order_status"], "partially_refunded"
        )
        self.assertEqual(partial_refund_response.data["refunded_amount"], "10.00")

        library_after_partial_refund_response = self.client.get("/api/v1/library/")
        self.assertEqual(
            library_after_partial_refund_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(library_after_partial_refund_response.data["count"], 1)

        full_refund_webhook_response = self.client.post(
            "/api/v1/payments/webhooks/",
            {
                "provider": "stripe",
                "event_id": "evt_e2e_refund",
                "event_type": "payment.refunded",
                "provider_payment_id": "pi_e2e",
                "refunded_amount": "29.99",
                "payload": {"step": "full-refund"},
            },
            format="json",
        )
        self.assertEqual(full_refund_webhook_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            full_refund_webhook_response.data["payment"]["status"], "refunded"
        )
        self.assertEqual(
            full_refund_webhook_response.data["payment"]["order_status"], "refunded"
        )

        library_after_refund_response = self.client.get("/api/v1/library/")
        self.assertEqual(library_after_refund_response.status_code, status.HTTP_200_OK)
        self.assertEqual(library_after_refund_response.data["count"], 0)

        download_after_refund_response = self.client.get(
            f"/api/v1/library/{product_id}/download/",
        )
        self.assertEqual(
            download_after_refund_response.status_code, status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            PurchaseAccess.objects.filter(
                buyer=self.buyer,
                product_id=product_id,
                is_active=True,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentWebhookEvent.objects.filter(
                event_id__in=[
                    "evt_e2e_processing",
                    "evt_e2e_success",
                    "evt_e2e_refund",
                ],
                is_processed=True,
            ).count(),
            3,
        )

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_secret")
    def test_stripe_webhook_signature_verification_processes_payment(self):
        product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Stripe Product",
            slug="stripe-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="15.00",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )
        order = Order.objects.create(
            buyer=self.buyer,
            order_number="ORD-STRIPE-TEST",
            status="pending_payment",
            subtotal_amount="15.00",
            platform_fee_amount="1.50",
            total_amount="15.00",
            currency="USD",
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            seller=self.seller,
            unit_price="15.00",
            final_price="15.00",
            platform_fee_amount="1.50",
            seller_net_amount="13.50",
        )
        payment = Payment.objects.create(
            order=order,
            provider="stripe",
            amount="15.00",
            currency="USD",
        )

        payload = {
            "id": "evt_stripe_success",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_stripe_success",
                    "metadata": {"payment_id": str(payment.id)},
                }
            },
        }
        body = json.dumps(payload).encode("utf-8")
        timestamp = int(time.time())
        signed_payload = f"{timestamp}.{body.decode('utf-8')}".encode("utf-8")
        signature = hmac.new(
            b"whsec_test_secret",
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        header = f"t={timestamp},v1={signature}"

        response = self.client.post(
            "/api/v1/payments/webhooks/stripe/",
            data=body,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=header,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["payment"]["status"], "succeeded")
        self.assertEqual(response.data["payment"]["order_status"], "fulfilled")

        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.provider_payment_id, "pi_stripe_success")
        self.assertEqual(payment.status, "succeeded")
        self.assertEqual(order.status, "fulfilled")
        self.assertEqual(
            PurchaseAccess.objects.filter(
                buyer=self.buyer,
                product=product,
                is_active=True,
            ).count(),
            1,
        )
