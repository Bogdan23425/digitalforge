from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.common.choices import ProductStatus
from apps.files.models import ProductImage


class PublicCatalogTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="public-catalog-seller@example.com",
            username="public-catalog-seller",
            password="StrongPass123",
            is_seller=True,
            email_verified=True,
        )
        self.category = Category.objects.create(name="UI Kits", slug="ui-kits-public")
        self.published_product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Published Kit",
            slug="published-kit",
            short_description="Published short",
            full_description="Published full description",
            product_type="ui_kit",
            base_price="39.99",
            currency="USD",
            status=ProductStatus.PUBLISHED,
        )
        self.draft_product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            title="Draft Kit",
            slug="draft-kit",
            short_description="Draft short",
            full_description="Draft full description",
            product_type="ui_kit",
            base_price="19.99",
            currency="USD",
            status=ProductStatus.DRAFT,
        )
        ProductImage.objects.create(
            product=self.published_product,
            image_url="https://example.com/cover.png",
            kind="cover",
            sort_order=0,
        )

    def test_public_catalog_only_exposes_published_products(self):
        list_response = self.client.get("/api/v1/products/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(list_response.data["results"][0]["slug"], "published-kit")

        detail_response = self.client.get("/api/v1/products/published-kit/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["slug"], "published-kit")
        self.assertEqual(
            detail_response.data["cover_image_url"], "https://example.com/cover.png"
        )

        draft_detail_response = self.client.get("/api/v1/products/draft-kit/")
        self.assertEqual(draft_detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_catalog_supports_category_and_search_filters(self):
        category_response = self.client.get("/api/v1/products/?category=ui-kits-public")
        self.assertEqual(category_response.status_code, status.HTTP_200_OK)
        self.assertEqual(category_response.data["count"], 1)

        search_response = self.client.get("/api/v1/products/?q=Published Kit")
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(search_response.data["count"], 1)
