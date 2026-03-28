from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class OrdersHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "orders", "status": "ok"})


urlpatterns = [
    path("health/", OrdersHealthView.as_view(), name="orders-health"),
]
