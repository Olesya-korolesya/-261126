from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.filters import ProductFilter
from blog.models import Category, Product
from blog.pagination import StandardResultsSetPagination
from blog.permissions import IsAdminOrReadOnly
from blog.serializers import (
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all().order_by("-created_at")
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("list", "popular"):
            return ProductListSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductWriteSerializer

    @extend_schema(
        summary="Получить популярные товары",
        responses={200: ProductListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        popular_products = self.filter_queryset(
            self.get_queryset().filter(is_popular=True)
        )
        page = self.paginate_queryset(popular_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(popular_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductsByCategoryAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Список товаров по ID категории",
        parameters=[
            OpenApiParameter(name="page", type=int, description="Номер страницы"),
            OpenApiParameter(name="page_size", type=int, description="Размер страницы"),
        ],
        responses={200: ProductListSerializer(many=True)},
    )
    def get(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        products = (
            Product.objects.select_related("category")
            .filter(category=category)
            .order_by("-created_at")
        )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
