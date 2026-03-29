from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
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
from apps.common.api.pagination import DefaultPageNumberPagination
from apps.common.api.serializers import DetailSerializer, ServiceHealthSerializer


class ModerationHealthView(APIView):
    permission_classes = []

    @extend_schema(
        operation_id="moderation_health",
        responses=ServiceHealthSerializer,
    )
    def get(self, request):
        return Response({"service": "moderation", "status": "ok"})


class ModerationQueueView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ModerationQueueItemSerializer
    queryset = Product.objects.none()
    pagination_class = DefaultPageNumberPagination

    @extend_schema(
        operation_id="moderation_queue",
        responses={200: ModerationQueueItemSerializer(many=True)},
    )
    def get(self, request):
        products = get_pending_review_products()
        page = self.paginate_queryset(products)
        if page is not None:
            return self.get_paginated_response(
                ModerationQueueItemSerializer(page, many=True).data
            )
        return Response(ModerationQueueItemSerializer(products, many=True).data)


class ApproveProductView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(
        operation_id="moderation_product_approve",
        request=ModerationActionSerializer,
        responses={200: ModerationQueueItemSerializer, 422: DetailSerializer},
    )
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

    @extend_schema(
        operation_id="moderation_product_request_changes",
        request=ModerationActionSerializer,
        responses={200: ModerationQueueItemSerializer, 422: DetailSerializer},
    )
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

    @extend_schema(
        operation_id="moderation_product_reject",
        request=ModerationActionSerializer,
        responses={200: ModerationQueueItemSerializer, 422: DetailSerializer},
    )
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
