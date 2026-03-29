from datetime import timedelta
from random import randint

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import EmailVerification, EmailVerificationStatus, User
from apps.accounts.tasks import send_verification_code_email

VERIFICATION_CODE_TTL_MINUTES = 10
VERIFICATION_RESEND_COOLDOWN_SECONDS = 60
VERIFICATION_MAX_ATTEMPTS = 5


def _generate_code() -> str:
    return f"{randint(0, 99999):05d}"


def _dispatch_verification_email(user: User, code: str) -> None:
    try:
        send_verification_code_email.delay(user.email, code)
    except Exception:
        send_verification_code_email(user.email, code)


@transaction.atomic
def create_email_verification(user: User) -> EmailVerification:
    code = _generate_code()
    now = timezone.now()

    user.email_verifications.filter(status=EmailVerificationStatus.PENDING).update(
        status=EmailVerificationStatus.CANCELED
    )

    verification = EmailVerification.objects.create(
        user=user,
        code_hash=make_password(code),
        expires_at=now + timedelta(minutes=VERIFICATION_CODE_TTL_MINUTES),
        resend_available_at=now
        + timedelta(seconds=VERIFICATION_RESEND_COOLDOWN_SECONDS),
    )
    _dispatch_verification_email(user, code)
    return verification


def verify_email_code(user: User, code: str) -> User:
    error_message = None

    with transaction.atomic():
        verification = (
            user.email_verifications.select_for_update()
            .filter(status=EmailVerificationStatus.PENDING)
            .first()
        )
        now = timezone.now()

        if verification is None:
            error_message = "No active verification flow."
        elif verification.expires_at <= now:
            verification.status = EmailVerificationStatus.EXPIRED
            verification.save(update_fields=["status"])
            error_message = "Verification code has expired."
        elif verification.attempts_count >= VERIFICATION_MAX_ATTEMPTS:
            verification.status = EmailVerificationStatus.FAILED
            verification.save(update_fields=["status"])
            error_message = "Verification attempts limit exceeded."
        elif not check_password(code, verification.code_hash):
            verification.attempts_count += 1
            if verification.attempts_count >= VERIFICATION_MAX_ATTEMPTS:
                verification.status = EmailVerificationStatus.FAILED
            verification.save(update_fields=["attempts_count", "status"])
            error_message = "Invalid verification code."
        else:
            verification.status = EmailVerificationStatus.VERIFIED
            verification.used_at = now
            verification.save(update_fields=["status", "used_at"])
            user.email_verified = True
            user.save(update_fields=["email_verified"])
            user.email_verifications.exclude(id=verification.id).filter(
                status=EmailVerificationStatus.PENDING
            ).update(status=EmailVerificationStatus.CANCELED)

    if error_message is not None:
        raise ValueError(error_message)

    return user


def resend_email_verification(user: User) -> EmailVerification:
    active_verification = user.email_verifications.filter(
        status=EmailVerificationStatus.PENDING
    ).first()
    if active_verification and active_verification.resend_available_at > timezone.now():
        raise ValueError("Resend cooldown has not passed yet.")
    return create_email_verification(user)
