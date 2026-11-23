import django_filters
from blog.models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(field_name="in_stock")

    class Meta:
        model = Product
        fields = ("min_price", "max_price", "in_stock")
