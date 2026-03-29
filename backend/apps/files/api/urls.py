from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class FilesHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"service": "files", "status": "ok"})


urlpatterns = [
    path("health/", FilesHealthView.as_view(), name="files-health"),
]
