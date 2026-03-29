from urllib.parse import quote

from django.conf import settings
from django.core import signing
from django.urls import reverse


DOWNLOAD_TOKEN_SALT = "library.download"


def build_signed_download_token(*, user_id, product_id, file_id):
    payload = {
        "user_id": str(user_id),
        "product_id": str(product_id),
        "file_id": str(file_id),
    }
    return signing.dumps(payload, salt=DOWNLOAD_TOKEN_SALT)


def parse_signed_download_token(*, token: str, max_age: int | None = None):
    max_age = max_age or settings.DOWNLOAD_URL_TTL_SECONDS
    return signing.loads(token, salt=DOWNLOAD_TOKEN_SALT, max_age=max_age)


def build_signed_download_url(*, request, token: str):
    path = reverse("library-secure-download", kwargs={"token": token})
    return request.build_absolute_uri(path)


def build_private_storage_redirect_url(*, storage_key: str):
    base_url = settings.PRIVATE_STORAGE_BASE_URL.rstrip("/")
    if not base_url:
        raise ValueError("Private storage base URL is not configured.")
    encoded_storage_key = quote(storage_key.lstrip("/"), safe="/")
    return f"{base_url}/{encoded_storage_key}"
