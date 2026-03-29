from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.complaints.api.serializers.complaints import (
    ComplaintCreateSerializer,
    ComplaintSerializer,
    ComplaintStatusUpdateSerializer,
)
from apps.complaints.models import Complaint
from apps.complaints.selectors import get_moderation_complaints, get_user_complaints
from apps.complaints.services import create_complaint, update_complaint_status
from apps.common.api.pagination import DefaultPageNumberPagination
from apps.common.api.serializers import DetailSerializer, ServiceHealthSerializer
from apps.moderation.permissions import IsModeratorOrAdmin


class ComplaintsHealthView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="complaints_health",
        responses=ServiceHealthSerializer,
    )
    def get(self, request):
        return Response({"service": "complaints", "status": "ok"})


class ComplaintListCreateView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.none()
    pagination_class = DefaultPageNumberPagination
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "complaints_write"

    def get_throttles(self):
        if self.request.method == "POST":
            return super().get_throttles()
        return []

    @extend_schema(
        operation_id="complaints_list",
        responses={200: ComplaintSerializer(many=True)},
    )
    def get(self, request):
        complaints = get_user_complaints(user=request.user)
        page = self.paginate_queryset(complaints)
        if page is not None:
            return self.get_paginated_response(
                ComplaintSerializer(page, many=True).data
            )
        return Response(ComplaintSerializer(complaints, many=True).data)

    @extend_schema(
        operation_id="complaints_create",
        request=ComplaintCreateSerializer,
        responses={201: ComplaintSerializer, 422: DetailSerializer},
    )
    def post(self, request):
        serializer = ComplaintCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            complaint = create_complaint(
                submitted_by=request.user,
                product=serializer.validated_data["product"],
                reason=serializer.validated_data["reason"],
                details=serializer.validated_data.get("details", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(
            ComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED
        )


class ModerationComplaintListView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.none()
    pagination_class = DefaultPageNumberPagination

    @extend_schema(
        operation_id="complaints_moderation_list",
        responses={200: ComplaintSerializer(many=True)},
    )
    def get(self, request):
        complaints = get_moderation_complaints()
        page = self.paginate_queryset(complaints)
        if page is not None:
            return self.get_paginated_response(
                ComplaintSerializer(page, many=True).data
            )
        return Response(ComplaintSerializer(complaints, many=True).data)


class ComplaintStatusUpdateView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.none()

    @extend_schema(
        operation_id="complaints_status_update",
        request=ComplaintStatusUpdateSerializer,
        responses={
            200: ComplaintSerializer,
            404: DetailSerializer,
        },
    )
    def patch(self, request, pk):
        serializer = ComplaintStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            complaint = Complaint.objects.select_related("product", "submitted_by").get(
                pk=pk
            )
        except Complaint.DoesNotExist:
            return Response(
                {"detail": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND
            )

        complaint = update_complaint_status(
            complaint=complaint,
            status_value=serializer.validated_data["status"],
        )
        return Response(ComplaintSerializer(complaint).data)
