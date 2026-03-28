from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class LibraryHealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"service": "library", "status": "ok"})


urlpatterns = [
    path("health/", LibraryHealthView.as_view(), name="library-health"),
]
