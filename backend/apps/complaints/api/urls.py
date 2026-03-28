from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class ComplaintsHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "complaints", "status": "ok"})


urlpatterns = [
    path("health/", ComplaintsHealthView.as_view(), name="complaints-health"),
]
