from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers.auth import (
    ProfileSerializer,
    ProfileUpdateSerializer,
)


class ProfileMeView(APIView):
    @extend_schema(
        operation_id="profile_me_retrieve",
        responses={200: ProfileSerializer},
    )
    def get(self, request):
        return Response(ProfileSerializer(request.user.profile).data)

    @extend_schema(
        operation_id="profile_me_update",
        request=ProfileUpdateSerializer,
        responses={200: ProfileSerializer},
    )
    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user.profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(request.user.profile).data)
