from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL-адрес")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена товара")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    is_popular = models.BooleanField(default=False, verbose_name="Востребованный товар")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
