from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product
from apps.common.choices import FileScanStatus, ProductStatus
from apps.files.models import ProductFile, ProductImage


class Command(BaseCommand):
    help = "Seed demo marketplace data for local development."

    def handle(self, *args, **options):
        user_model = get_user_model()

        seller, _ = user_model.objects.get_or_create(
            email="demo-seller@digitalforge.local",
            defaults={
                "username": "demo-seller",
                "is_seller": True,
                "email_verified": True,
            },
        )
        seller.is_seller = True
        seller.email_verified = True
        seller.set_password("DemoPass123")
        seller.save()

        moderator, _ = user_model.objects.get_or_create(
            email="demo-moderator@digitalforge.local",
            defaults={
                "username": "demo-moderator",
                "is_moderator": True,
                "email_verified": True,
            },
        )
        moderator.is_moderator = True
        moderator.email_verified = True
        moderator.set_password("DemoPass123")
        moderator.save()

        buyer, _ = user_model.objects.get_or_create(
            email="demo-buyer@digitalforge.local",
            defaults={
                "username": "demo-buyer",
                "email_verified": True,
            },
        )
        buyer.email_verified = True
        buyer.set_password("DemoPass123")
        buyer.save()

        ui_kits, _ = Category.objects.get_or_create(
            slug="demo-ui-kits",
            defaults={"name": "Demo UI Kits", "description": "Seeded demo category."},
        )
        templates, _ = Category.objects.get_or_create(
            slug="demo-templates",
            defaults={"name": "Demo Templates", "description": "Seeded demo category."},
        )

        products = [
            {
                "category": ui_kits,
                "title": "SaaS Dashboard Kit",
                "slug": "demo-saas-dashboard-kit",
                "short_description": "Admin dashboard kit for SaaS products.",
                "full_description": "A seeded published product for demos and API testing.",
                "product_type": "ui_kit",
                "base_price": Decimal("39.99"),
                "currency": "USD",
            },
            {
                "category": templates,
                "title": "Landing Page Template",
                "slug": "demo-landing-page-template",
                "short_description": "Responsive marketing template.",
                "full_description": "A seeded published template for local demo environments.",
                "product_type": "template",
                "base_price": Decimal("24.99"),
                "currency": "USD",
            },
        ]

        for item in products:
            product, _ = Product.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    **item,
                    "seller": seller,
                    "status": ProductStatus.PUBLISHED,
                },
            )
            ProductImage.objects.get_or_create(
                product=product,
                kind="cover",
                defaults={
                    "image_url": f"https://example.com/{product.slug}-cover.png",
                    "sort_order": 0,
                },
            )
            ProductFile.objects.get_or_create(
                product=product,
                storage_key=f"products/demo/{product.slug}.zip",
                defaults={
                    "file_name": f"{product.slug}.zip",
                    "mime_type": "application/zip",
                    "file_size": 1024,
                    "checksum": f"seed-{product.slug}",
                    "is_current": True,
                    "scan_status": FileScanStatus.CLEAN,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Accounts:")
        self.stdout.write("  seller: demo-seller@digitalforge.local / DemoPass123")
        self.stdout.write(
            "  moderator: demo-moderator@digitalforge.local / DemoPass123"
        )
        self.stdout.write("  buyer: demo-buyer@digitalforge.local / DemoPass123")
