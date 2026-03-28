from django.db import transaction

from apps.accounts.models import User
from apps.accounts.services.email_verification import create_email_verification


@transaction.atomic
def register_user(
    *,
    email: str,
    username: str,
    password: str,
) -> User:
    user = User.objects.create_user(
        email=email,
        username=username,
        password=password,
    )
    create_email_verification(user)
    return user
