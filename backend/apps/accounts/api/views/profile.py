from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers.auth import (
    ProfileSerializer,
    ProfileUpdateSerializer,
)


class ProfileMeView(APIView):
    def get(self, request):
        return Response(ProfileSerializer(request.user.profile).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user.profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(request.user.profile).data)
