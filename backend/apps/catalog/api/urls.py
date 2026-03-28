from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class CatalogHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "catalog", "status": "ok"})


urlpatterns = [
    path("health/", CatalogHealthView.as_view(), name="catalog-health"),
]
