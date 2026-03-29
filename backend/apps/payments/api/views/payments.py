from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.api.serializers.payments import (
    PaymentActionSerializer,
    PaymentRefundSerializer,
    PaymentSerializer,
    PaymentWebhookSerializer,
)
from apps.payments.selectors.payments import get_user_payment_by_id, get_user_payments
from apps.payments.services.payments import (
    mark_payment_failed,
    mark_payment_partially_refunded,
    mark_payment_refunded,
    mark_payment_succeeded,
)
from apps.payments.services.webhooks import process_payment_webhook
from apps.payments.services.stripe_webhooks import verify_and_process_stripe_webhook


class PaymentsHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"service": "payments", "status": "ok"})


class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = get_user_payments(user=request.user)
        return Response(PaymentSerializer(payments, many=True).data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        payment = get_user_payment_by_id(user=request.user, payment_id=pk)
        if payment is None:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(PaymentSerializer(payment).data)


class PaymentSimulateSuccessView(APIView):
    permission_classes = [IsAuthenticated]

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

    def post(self, request):
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
