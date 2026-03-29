from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.catalog.permissions import IsProductOwnerOrAdmin, IsSellerOrAdmin
from apps.files.api.serializers.uploads import (
    ProductFileCreateSerializer,
    ProductFileSerializer,
    ProductImageCreateSerializer,
    ProductImageSerializer,
)
from apps.files.models import ProductFile, ProductImage
from apps.files.services import add_product_file, add_product_image
from apps.common.api.serializers import DetailSerializer


class SellerProductImageListCreateView(APIView):
    permission_classes = [IsSellerOrAdmin, IsProductOwnerOrAdmin]

    def get_product(self, request, pk):
        product = Product.objects.get(pk=pk, is_deleted=False)
        self.check_object_permissions(request, product)
        return product

    @extend_schema(
        operation_id="seller_product_images_list",
        responses={200: ProductImageSerializer(many=True)},
    )
    def get(self, request, pk):
        product = self.get_product(request, pk)
        images = product.images.order_by("sort_order", "created_at")
        return Response(ProductImageSerializer(images, many=True).data)

    @extend_schema(
        operation_id="seller_product_images_create",
        request=ProductImageCreateSerializer,
        responses={201: ProductImageSerializer},
    )
    def post(self, request, pk):
        product = self.get_product(request, pk)
        serializer = ProductImageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = add_product_image(product=product, **serializer.validated_data)
        return Response(
            ProductImageSerializer(image).data,
            status=status.HTTP_201_CREATED,
        )


class SellerProductImageDeleteView(APIView):
    permission_classes = [IsSellerOrAdmin, IsProductOwnerOrAdmin]

    @extend_schema(
        operation_id="seller_product_images_delete",
        request=None,
        responses={
            204: OpenApiResponse(description="Image deleted."),
            404: DetailSerializer,
        },
    )
    def delete(self, request, pk, image_id):
        product = Product.objects.get(pk=pk, is_deleted=False)
        self.check_object_permissions(request, product)
        ProductImage.objects.filter(id=image_id, product=product).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SellerProductFileListCreateView(APIView):
    permission_classes = [IsSellerOrAdmin, IsProductOwnerOrAdmin]

    def get_product(self, request, pk):
        product = Product.objects.get(pk=pk, is_deleted=False)
        self.check_object_permissions(request, product)
        return product

    @extend_schema(
        operation_id="seller_product_files_list",
        responses={200: ProductFileSerializer(many=True)},
    )
    def get(self, request, pk):
        product = self.get_product(request, pk)
        files = product.files.order_by("-is_current", "-created_at")
        return Response(ProductFileSerializer(files, many=True).data)

    @extend_schema(
        operation_id="seller_product_files_create",
        request=ProductFileCreateSerializer,
        responses={201: ProductFileSerializer},
    )
    def post(self, request, pk):
        product = self.get_product(request, pk)
        serializer = ProductFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_file = add_product_file(product=product, **serializer.validated_data)
        return Response(
            ProductFileSerializer(product_file).data,
            status=status.HTTP_201_CREATED,
        )


class SellerProductFileDeleteView(APIView):
    permission_classes = [IsSellerOrAdmin, IsProductOwnerOrAdmin]

    @extend_schema(
        operation_id="seller_product_files_delete",
        request=None,
        responses={
            204: OpenApiResponse(description="File deleted."),
            404: DetailSerializer,
        },
    )
    def delete(self, request, pk, file_id):
        product = Product.objects.get(pk=pk, is_deleted=False)
        self.check_object_permissions(request, product)
        ProductFile.objects.filter(id=file_id, product=product).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
