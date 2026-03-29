from django.conf import settings
from django.http import HttpResponseRedirect
from django.core import signing
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.library.api.serializers.library import (
    DownloadAuthorizationSerializer,
    PurchaseAccessSerializer,
)
from apps.library.selectors.access import (
    get_user_purchase_access_for_product,
    get_user_purchase_accesses,
)
from apps.library.services import (
    build_private_storage_redirect_url,
    build_signed_download_token,
    build_signed_download_url,
    get_current_downloadable_file,
    parse_signed_download_token,
)


class LibraryHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"service": "library", "status": "ok"})


class LibraryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accesses = get_user_purchase_accesses(user=request.user)
        return Response(PurchaseAccessSerializer(accesses, many=True).data)


class LibraryDownloadAuthorizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        purchase_access = get_user_purchase_access_for_product(
            user=request.user,
            product_id=product_id,
        )
        if purchase_access is None:
            return Response(
                {"detail": "Purchase access not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            product_file = get_current_downloadable_file(
                purchase_access=purchase_access
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        payload = {
            "product_id": purchase_access.product.id,
            "title": purchase_access.product.title,
            "file_name": product_file.file_name,
            "mime_type": product_file.mime_type,
            "file_size": product_file.file_size,
            "expires_in": settings.DOWNLOAD_URL_TTL_SECONDS,
            "download_url": build_signed_download_url(
                request=request,
                token=build_signed_download_token(
                    user_id=request.user.id,
                    product_id=purchase_access.product.id,
                    file_id=product_file.id,
                ),
            ),
        }
        return Response(DownloadAuthorizationSerializer(payload).data)


class LibrarySecureDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, token):
        try:
            payload = parse_signed_download_token(token=token)
        except signing.BadSignature:
            return Response(
                {"detail": "Download token is invalid or expired."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if payload["user_id"] != str(request.user.id):
            return Response(
                {"detail": "Download token does not belong to the current user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        purchase_access = get_user_purchase_access_for_product(
            user=request.user,
            product_id=payload["product_id"],
        )
        if purchase_access is None:
            return Response(
                {"detail": "Purchase access not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            product_file = get_current_downloadable_file(
                purchase_access=purchase_access
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        if str(product_file.id) != payload["file_id"]:
            return Response(
                {"detail": "Download token does not match the current product file."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            redirect_url = build_private_storage_redirect_url(
                storage_key=product_file.storage_key
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return HttpResponseRedirect(redirect_url)
