from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.notifications.api.serializers import NotificationSerializer
from apps.notifications.models import Notification
from apps.notifications.services import (
    mark_all_notifications_read,
    mark_notification_read,
)
from apps.common.api.pagination import DefaultPageNumberPagination
from apps.common.api.serializers import (
    DetailSerializer,
    ServiceHealthSerializer,
    UpdatedCountSerializer,
)


class NotificationsHealthView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="notifications_health",
        responses=ServiceHealthSerializer,
    )
    def get(self, request):
        return Response({"service": "notifications", "status": "ok"})


class NotificationListView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.none()
    pagination_class = DefaultPageNumberPagination

    @extend_schema(
        operation_id="notifications_list",
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by(
            "-created_at"
        )
        page = self.paginate_queryset(notifications)
        if page is not None:
            return self.get_paginated_response(
                NotificationSerializer(page, many=True).data
            )
        return Response(NotificationSerializer(notifications, many=True).data)


class NotificationReadView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.none()
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "notification_write"

    @extend_schema(
        operation_id="notifications_read",
        request=None,
        responses={200: NotificationSerializer, 404: DetailSerializer},
    )
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        notification = mark_notification_read(notification=notification)
        return Response(NotificationSerializer(notification).data)


class NotificationReadAllView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatedCountSerializer
    queryset = Notification.objects.none()
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "notification_write"

    @extend_schema(
        operation_id="notifications_read_all",
        request=None,
        responses={200: UpdatedCountSerializer},
    )
    def post(self, request):
        updated_count = mark_all_notifications_read(user=request.user)
        return Response({"updated_count": updated_count})
