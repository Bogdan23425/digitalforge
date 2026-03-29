# Deployment

## Local Docker Stack

The repository includes `docker-compose.yml` for local startup:

```powershell
docker compose up --build
```

Services:
- `web` - Django + Gunicorn
- `worker` - Celery worker
- `db` - PostgreSQL 16
- `redis` - Redis 7

Available URLs:
- `http://127.0.0.1:8000/api/docs/swagger/`
- `http://127.0.0.1:8000/api/docs/redoc/`
- `http://127.0.0.1:8000/admin/`

## Settings

Docker uses:
- `backend/Dockerfile`
- `backend/config/settings/docker.py`

Main environment variables:
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

Environment template:
- `backend/.env.example`

## Notes

- The compose stack is meant for local development and demos
- production deployment still needs a reverse proxy, private object storage, and proper secret management
- the secure download flow already uses a signed application URL and can redirect to a private storage endpoint
