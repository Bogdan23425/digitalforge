from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.serializers.products import (
    CategorySerializer,
    PublicProductDetailSerializer,
    PublicProductListSerializer,
    SellerProductCreateSerializer,
    SellerProductDetailSerializer,
    SellerProductListSerializer,
    SellerProductUpdateSerializer,
)
from apps.catalog.models import Category, Product
from apps.catalog.permissions import IsProductOwnerOrAdmin, IsSellerOrAdmin
from apps.catalog.selectors.products import get_public_products, get_seller_products
from apps.catalog.services.products import (
    create_product,
    submit_product_for_review,
    update_product,
)
from apps.common.api.pagination import DefaultPageNumberPagination


class CatalogHealthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"service": "catalog", "status": "ok"})


class CategoryListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by("sort_order", "name")


class PublicProductListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicProductListSerializer
    pagination_class = DefaultPageNumberPagination

    def get_queryset(self):
        queryset = get_public_products()
        category_slug = self.request.query_params.get("category")
        search_query = self.request.query_params.get("q")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(short_description__icontains=search_query)
                | Q(full_description__icontains=search_query)
            )
        return queryset


class PublicProductDetailView(RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return get_public_products()


class SellerProductListCreateView(APIView):
    permission_classes = [IsSellerOrAdmin]

    def get(self, request):
        products = get_seller_products(seller_id=request.user.id)
        return Response(SellerProductListSerializer(products, many=True).data)

    def post(self, request):
        serializer = SellerProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = create_product(seller=request.user, **serializer.validated_data)
        return Response(
            SellerProductDetailSerializer(product).data,
            status=status.HTTP_201_CREATED,
        )


class SellerProductDetailView(APIView):
    permission_classes = [IsSellerOrAdmin, IsProductOwnerOrAdmin]

    def get_object(self, request, pk):
        product = Product.objects.select_related("category").get(
            pk=pk, is_deleted=False
        )
        self.check_object_permissions(request, product)
        return product

    def get(self, request, pk):
        product = self.get_object(request, pk)
        return Response(SellerProductDetailSerializer(product).data)

    def patch(self, request, pk):
        product = self.get_object(request, pk)
        serializer = SellerProductUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = update_product(product=product, **serializer.validated_data)
        return Response(SellerProductDetailSerializer(product).data)


class SellerProductSubmitView(APIView):
    permission_classes = [IsSellerOrAdmin, IsProductOwnerOrAdmin]

    def post(self, request, pk):
        product = Product.objects.get(pk=pk, is_deleted=False)
        self.check_object_permissions(request, product)
        try:
            product = submit_product_for_review(product=product)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response(SellerProductDetailSerializer(product).data)
