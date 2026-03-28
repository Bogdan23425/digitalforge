from celery import shared_task
from django.core.mail import send_mail

from django.conf import settings


@shared_task
def send_verification_code_email(email: str, code: str) -> None:
    send_mail(
        subject="Verify your email",
        message=f"Your DigitalForge verification code is: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
