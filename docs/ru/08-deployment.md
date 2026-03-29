# Deployment

## Локальный Docker Stack

В репозитории есть `docker-compose.yml` для локального запуска:

```powershell
docker compose up --build
```

Что поднимается:
- `web` - Django + Gunicorn
- `worker` - Celery worker
- `db` - PostgreSQL 16
- `redis` - Redis 7

После старта доступны:
- `http://127.0.0.1:8000/api/docs/swagger/`
- `http://127.0.0.1:8000/api/docs/redoc/`
- `http://127.0.0.1:8000/admin/`

## Настройки

Для Docker используется:
- `backend/Dockerfile`
- `backend/config/settings/docker.py`

Основные env vars:
- `DJANGO_SETTINGS_MODULE`
- `DJANGO_SECRET_KEY`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_URL`
- `PRIVATE_STORAGE_BASE_URL`
- `STRIPE_WEBHOOK_SECRET`

Шаблон переменных:
- `backend/.env.example`

## Замечания

- Compose предназначен для local development и demo
- production deployment потребует отдельного reverse proxy, private object storage и secret management
- secure download flow уже использует signed application URL и может быть направлен в private storage endpoint
