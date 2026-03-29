# DigitalForge

DigitalForge is a backend for a digital products marketplace.
The project uses Django and PostgreSQL and focuses on clear domain boundaries,
secure file delivery, payment processing, moderation, and concise
documentation in Russian and English.

## Documentation

- [Docs Index](./docs/README.md)
- [Russian Docs](./docs/ru/README.md)
- [English Docs](./docs/en/README.md)

## Local Start

```powershell
cd backend
python -m pip install -r requirements\local.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Useful local URLs:
- `http://127.0.0.1:8000/api/docs/swagger/`
- `http://127.0.0.1:8000/api/docs/redoc/`
- `http://127.0.0.1:8000/admin/`

Environment template:
- `backend/.env.example`

## Docker

```powershell
docker compose up --build
```

This starts:
- Django + Gunicorn
- Celery worker
- PostgreSQL
- Redis

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

## Demo Accounts

- `demo-seller@digitalforge.local / DemoPass123`
- `demo-moderator@digitalforge.local / DemoPass123`
- `demo-buyer@digitalforge.local / DemoPass123`

## CI

GitHub Actions runs:
- `black --check`
- `ruff check`
- `python manage.py check`
- `python -m pytest`
