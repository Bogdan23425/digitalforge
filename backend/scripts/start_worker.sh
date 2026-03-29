#!/bin/sh
set -e

python scripts/wait_for_db.py

exec celery -A config.celery worker --loglevel=info
