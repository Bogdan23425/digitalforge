FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements/local.txt \
    && python -m pip install -r requirements/production.txt

COPY . .

RUN chmod +x scripts/start_web.sh scripts/start_worker.sh scripts/wait_for_db.py

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
