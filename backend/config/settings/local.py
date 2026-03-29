from .base import *  # noqa: F403,F401

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
