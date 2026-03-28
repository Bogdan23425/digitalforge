from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class ModerationHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "moderation", "status": "ok"})


urlpatterns = [
    path("health/", ModerationHealthView.as_view(), name="moderation-health"),
]
