from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers.auth import (
    LoginSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserMeSerializer,
    VerifyEmailSerializer,
)
from apps.accounts.services import (
    register_user,
    resend_email_verification,
    verify_email_code,
)
from apps.audit.services import write_audit_log
from apps.common.api.serializers import DetailSerializer, ServiceHealthSerializer


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="accounts_health",
        responses=ServiceHealthSerializer,
    )
    def get(self, request):
        return Response({"service": "accounts", "status": "ok"})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="auth_csrf",
        responses=DetailSerializer,
    )
    def get(self, request):
        return Response({"detail": "CSRF cookie set."})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

    @extend_schema(
        operation_id="auth_register",
        request=RegisterSerializer,
        responses={201: UserMeSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(
            email=serializer.validated_data["email"],
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        login(request, user)
        write_audit_log(
            actor_user=user,
            action_type="auth.register",
            entity_type="user",
            entity_id=user.id,
            metadata={"email": user.email},
        )
        return Response(UserMeSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    @extend_schema(
        operation_id="auth_login",
        request=LoginSerializer,
        responses={200: UserMeSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        write_audit_log(
            actor_user=user,
            action_type="auth.login",
            entity_type="user",
            entity_id=user.id,
        )
        return Response(UserMeSerializer(user).data)


class LogoutView(APIView):
    @extend_schema(
        operation_id="auth_logout",
        request=None,
        responses={204: OpenApiResponse(description="Logged out.")},
    )
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        logout(request)
        if user is not None:
            write_audit_log(
                actor_user=user,
                action_type="auth.logout",
                entity_type="user",
                entity_id=user.id,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    @extend_schema(
        operation_id="auth_me",
        responses={200: UserMeSerializer},
    )
    def get(self, request):
        return Response(UserMeSerializer(request.user).data)


class VerifyEmailView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_verify_email"

    @extend_schema(
        operation_id="auth_verify_email",
        request=VerifyEmailSerializer,
        responses={
            200: UserMeSerializer,
            422: DetailSerializer,
        },
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = verify_email_code(request.user, serializer.validated_data["code"])
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        write_audit_log(
            actor_user=user,
            action_type="auth.email_verified",
            entity_type="user",
            entity_id=user.id,
        )
        return Response(UserMeSerializer(user).data)


class ResendVerificationCodeView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_resend_verification"

    @extend_schema(
        operation_id="auth_resend_verification_code",
        request=ResendVerificationSerializer,
        responses={
            204: OpenApiResponse(description="Verification code re-sent."),
            422: DetailSerializer,
        },
    )
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            resend_email_verification(request.user)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
