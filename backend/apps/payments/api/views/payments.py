from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.payments.api.serializers.payments import (
    PaymentActionSerializer,
    PaymentRefundSerializer,
    PaymentSerializer,
    PaymentWebhookSerializer,
)
from apps.payments.models import Payment
from apps.payments.selectors.payments import get_user_payment_by_id, get_user_payments
from apps.payments.services.payments import (
    mark_payment_failed,
    mark_payment_partially_refunded,
    mark_payment_refunded,
    mark_payment_succeeded,
)
from apps.payments.services.webhooks import process_payment_webhook
from apps.payments.services.stripe_webhooks import verify_and_process_stripe_webhook
from apps.common.api.pagination import DefaultPageNumberPagination
from apps.common.api.serializers import DetailSerializer, ServiceHealthSerializer


class PaymentsHealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(operation_id="payments_health", responses=ServiceHealthSerializer)
    def get(self, request):
        return Response({"service": "payments", "status": "ok"})


class PaymentListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.none()
    pagination_class = DefaultPageNumberPagination

    @extend_schema(
        operation_id="payments_list",
        responses={200: PaymentSerializer(many=True)},
    )
    def get(self, request):
        payments = get_user_payments(user=request.user)
        page = self.paginate_queryset(payments)
        if page is not None:
            return self.get_paginated_response(PaymentSerializer(page, many=True).data)
        return Response(PaymentSerializer(payments, many=True).data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="payments_detail",
        responses={200: PaymentSerializer, 404: DetailSerializer},
    )
    def get(self, request, pk):
        payment = get_user_payment_by_id(user=request.user, payment_id=pk)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(PaymentSerializer(payment).data)


class PaymentSimulateSuccessView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment_actions"

    @extend_schema(
        operation_id="payments_simulate_success",
        request=PaymentActionSerializer,
        responses={
            200: PaymentSerializer,
            404: DetailSerializer,
            422: DetailSerializer,
        },
    )
    def post(self, request, pk):
        payment = get_user_payment_by_id(user=request.user, payment_id=pk)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PaymentActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = mark_payment_succeeded(
                payment=payment,
                provider_payment_id=serializer.validated_data.get(
                    "provider_payment_id", ""
                ),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(PaymentSerializer(payment).data)


class PaymentSimulateFailureView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment_actions"

    @extend_schema(
        operation_id="payments_simulate_failure",
        request=None,
        responses={
            200: PaymentSerializer,
            404: DetailSerializer,
            422: DetailSerializer,
        },
    )
    def post(self, request, pk):
        payment = get_user_payment_by_id(user=request.user, payment_id=pk)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            payment = mark_payment_failed(payment=payment)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(PaymentSerializer(payment).data)


class PaymentSimulatePartialRefundView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment_actions"

    @extend_schema(
        operation_id="payments_simulate_partial_refund",
        request=PaymentRefundSerializer,
        responses={
            200: PaymentSerializer,
            404: DetailSerializer,
            422: DetailSerializer,
        },
    )
    def post(self, request, pk):
        payment = get_user_payment_by_id(user=request.user, payment_id=pk)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PaymentRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = mark_payment_partially_refunded(
                payment=payment,
                refunded_amount=serializer.validated_data["refunded_amount"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(PaymentSerializer(payment).data)


class PaymentSimulateRefundView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment_actions"

    @extend_schema(
        operation_id="payments_simulate_refund",
        request=PaymentRefundSerializer,
        responses={
            200: PaymentSerializer,
            404: DetailSerializer,
            422: DetailSerializer,
        },
    )
    def post(self, request, pk):
        payment = get_user_payment_by_id(user=request.user, payment_id=pk)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PaymentRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = mark_payment_refunded(
                payment=payment,
                refunded_amount=serializer.validated_data.get("refunded_amount"),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(PaymentSerializer(payment).data)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment_webhook"

    @extend_schema(
        operation_id="payments_webhook",
        request=PaymentWebhookSerializer,
        responses={
            200: OpenApiResponse(description="Webhook processed."),
            422: DetailSerializer,
        },
    )
    def post(self, request):
        if not settings.ENABLE_GENERIC_PAYMENT_WEBHOOK:
            return Response(
                {"detail": "Generic payment webhook is disabled."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = process_payment_webhook(**serializer.validated_data)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        payment = result["payment"]
        return Response(
            {
                "event_id": result["event"].event_id,
                "created": result["created"],
                "processed": result["processed"],
                "payment": PaymentSerializer(payment).data if payment else None,
            }
        )


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment_webhook"

    @extend_schema(
        operation_id="payments_stripe_webhook",
        request=None,
        responses={
            200: OpenApiResponse(description="Stripe webhook processed."),
            400: DetailSerializer,
            422: DetailSerializer,
            503: DetailSerializer,
        },
    )
    def post(self, request):
        import stripe

        signature = request.headers.get("Stripe-Signature", "")
        try:
            result = verify_and_process_stripe_webhook(
                payload=request.body,
                signature=signature,
            )
        except ValueError as exc:
            status_code = (
                status.HTTP_503_SERVICE_UNAVAILABLE
                if "not configured" in str(exc)
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            return Response({"detail": str(exc)}, status=status_code)
        except stripe.error.SignatureVerificationError:
            return Response(
                {"detail": "Invalid Stripe signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        payment = result["payment"]
        return Response(
            {
                "event_id": result["event"].event_id,
                "created": result["created"],
                "processed": result["processed"],
                "payment": PaymentSerializer(payment).data if payment else None,
            }
        )
