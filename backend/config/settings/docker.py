from .base import *  # noqa: F403,F401

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "web", "testserver"]  # noqa: F405

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
ENABLE_GENERIC_PAYMENT_WEBHOOK = True  # noqa: F405
