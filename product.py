from rest_framework import serializers
from blog.models import Category, Product
from .base import CategoryNestedSerializer

class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryNestedSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "price", "in_stock", "is_popular", "category")

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryNestedSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "in_stock",
            "is_popular",
            "category",
            "created_at",
        )

class ProductWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "Название товара обязательно.",
            "blank": "Название товара не может быть пустым.",
        },
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "in_stock", "is_popular", "category")

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена товара не может быть отрицательной.")
        return value