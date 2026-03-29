from django.urls import path

from apps.accounts.api.views import (
    CsrfView,
    HealthView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    ResendVerificationCodeView,
    VerifyEmailView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="accounts-health"),
    path("csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("verify-email/", VerifyEmailView.as_view(), name="auth-verify-email"),
    path(
        "resend-verification-code/",
        ResendVerificationCodeView.as_view(),
        name="auth-resend-verification-code",
    ),
]
