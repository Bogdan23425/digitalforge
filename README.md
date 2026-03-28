# DigitalForge

DigitalForge is a backend for a digital products marketplace.
The project uses Django and PostgreSQL and focuses on clear domain boundaries,
secure file delivery, payment processing, moderation, and concise
documentation in Russian and English.

## Documentation

- [Docs Index](./docs/README.md)
- [Russian Docs](./docs/ru/README.md)
- [English Docs](./docs/en/README.md)

## Product Focus

- Sellers publish digital products
- Buyers purchase and securely download files
- Staff moderates content and handles abuse cases
- The architecture is built around explicit domain modules and service-layer flows

## Core Stack

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Object storage for private files
- Stripe as the first payment provider
