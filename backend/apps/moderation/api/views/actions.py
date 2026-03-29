from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.moderation.api.serializers.actions import (
    ModerationActionSerializer,
    ModerationQueueItemSerializer,
)
from apps.moderation.permissions import IsModeratorOrAdmin
from apps.moderation.selectors.queue import get_pending_review_products
from apps.moderation.services import approve_product, reject_product, request_changes


class ModerationHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "moderation", "status": "ok"})


class ModerationQueueView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    def get(self, request):
        products = get_pending_review_products()
        return Response(ModerationQueueItemSerializer(products, many=True).data)


class ApproveProductView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, pk):
        serializer = ModerationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(pk=pk, is_deleted=False)
        try:
            product = approve_product(
                product=product,
                actor_user=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(ModerationQueueItemSerializer(product).data)


class RequestChangesView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, pk):
        serializer = ModerationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(pk=pk, is_deleted=False)
        try:
            product = request_changes(
                product=product,
                actor_user=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(ModerationQueueItemSerializer(product).data)


class RejectProductView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, pk):
        serializer = ModerationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(pk=pk, is_deleted=False)
        try:
            product = reject_product(
                product=product,
                actor_user=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(ModerationQueueItemSerializer(product).data)
