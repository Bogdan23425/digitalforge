from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class PaymentsHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "payments", "status": "ok"})


urlpatterns = [
    path("health/", PaymentsHealthView.as_view(), name="payments-health"),
]
