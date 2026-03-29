#!/bin/sh
set -e

python scripts/wait_for_db.py
python manage.py migrate
python manage.py seed_demo_data
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
