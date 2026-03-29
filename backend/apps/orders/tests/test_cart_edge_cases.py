from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus
from apps.library.models import PurchaseAccess
from apps.orders.models import Order, OrderItem


class CartEdgeCaseTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="cart-seller@example.com",
            username="cart-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.buyer = User.objects.create_user(
            email="cart-buyer@example.com",
            username="cart-buyer",
            password="StrongPass123",
            email_verified=True,
        )
        self.category = Category.objects.create(name="Cart Cases", slug="cart-cases")
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Cart Product",
            slug="cart-product",
            short_description="Short",
            full_description="Full",
            product_type="template",
            base_price="19.99",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )

    def test_cart_rejects_own_product_and_duplicate_item(self):
        self.client.force_authenticate(user=self.seller)
        own_product_response = self.client.post(
            "/api/v1/cart/items/",
            {"product_id": str(self.product.id)},
            format="json",
        )
        self.assertEqual(
            own_product_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            own_product_response.data["detail"], "You cannot buy your own product."
        )

        self.client.force_authenticate(user=self.buyer)
        first_add_response = self.client.post(
            "/api/v1/cart/items/",
            {"product_id": str(self.product.id)},
            format="json",
        )
        self.assertEqual(first_add_response.status_code, status.HTTP_201_CREATED)

        duplicate_add_response = self.client.post(
            "/api/v1/cart/items/",
            {"product_id": str(self.product.id)},
            format="json",
        )
        self.assertEqual(
            duplicate_add_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(
            duplicate_add_response.data["detail"], "Product is already in the cart."
        )

    def test_cart_rejects_product_already_owned_by_buyer(self):
        order = Order.objects.create(
            buyer=self.buyer,
            order_number="ORD-CART-OWNED",
            status="fulfilled",
            subtotal_amount="19.99",
            platform_fee_amount="2.00",
            total_amount="19.99",
            currency="USD",
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            seller=self.seller,
            unit_price="19.99",
            final_price="19.99",
            platform_fee_amount="2.00",
            seller_net_amount="17.99",
        )
        PurchaseAccess.objects.create(
            order_item=order_item,
            buyer=self.buyer,
            product=self.product,
        )

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(
            "/api/v1/cart/items/",
            {"product_id": str(self.product.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["detail"], "You already own this product.")
