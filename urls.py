from django.urls import include, path
from rest_framework.routers import DefaultRouter
from blog.views import ProductsByCategoryAPIView, ProductViewSet

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

router = DefaultRouter()
router.register(r"blog", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "categories/<int:category_id>/products/",
        ProductsByCategoryAPIView.as_view(),
        name="products-by-category",
    ),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
