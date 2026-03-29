from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.common.api.serializers import ServiceHealthSerializer


class FilesHealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(operation_id="files_health", responses=ServiceHealthSerializer)
    def get(self, request):
        return Response({"service": "files", "status": "ok"})


urlpatterns = [
    path("health/", FilesHealthView.as_view(), name="files-health"),
]
