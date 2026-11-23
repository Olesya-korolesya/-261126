from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from blog.models import Category, Product

User = get_user_model()

class ProductAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="password123"
        )
        self.user = User.objects.create_user(
            username="user", email="user@test.com", password="password123"
        )

        self.cat_electronics = Category.objects.create(
            name="Бытовая электроника", slug="consumer electronics"
        )
        self.cat_books = Category.objects.create(name="Книги", slug="books")

        self.p1 = Product.objects.create(
            name="Компьютер",
            description="Игровой компьютер",
            price=Decimal("150000.00"),
            in_stock=True,
            is_popular=True,
            category=self.cat_electronics,
        )
        self.p2 = Product.objects.create(
            name="Айфон",
            description="Флагман",
            price=Decimal("200000.00"),
            in_stock=False,
            is_popular=False,
            category=self.cat_electronics,
        )
        self.p3 = Product.objects.create(
            name="Книга по программированию",
            description="Изучаем DRF",
            price=Decimal("1500.00"),
            in_stock=True,
            is_popular=True,
            category=self.cat_books,
        )

        self.list_url = reverse("product-list")
        self.popular_url = reverse("product-popular")

    def test_list_and_detail_serializers(self):
        list_res = self.client.get(self.list_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertIn("results", list_res.data)

        first_item = list_res.data["results"][0]
        self.assertNotIn("description", first_item)
        self.assertEqual(first_item["category"]["name"], self.cat_books.name)

        detail_url = reverse("product-detail", args=[self.p1.id])
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertIn("description", detail_res.data)
        self.assertIn("created_at", detail_res.data)

    def test_filtering_by_price_and_stock(self):
        res = self.client.get(
            self.list_url, {"min_price": 1000, "max_price": 50000, "in_stock": "true"}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["name"], "Книга по программированию")

    def test_popular_products_action(self):
        res = self.client.get(self.popular_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)

    def test_products_by_category_apiview(self):
        url = reverse("products-by-category", args=[self.cat_electronics.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)

    def test_permissions_on_create(self):
        payload = {
            "name": "Планшет",
            "price": "30000.00",
            "category": self.cat_electronics.id,
        }

        res_anon = self.client.post(self.list_url, payload)
        self.assertEqual(res_anon.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        res_user = self.client.post(self.list_url, payload)
        self.assertEqual(res_user.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.post(self.list_url, payload)
        self.assertEqual(res_admin.status_code, status.HTTP_201_CREATED)

    def test_validation_rules(self):
        self.client.force_authenticate(user=self.admin)

        res_neg_price = self.client.post(
            self.list_url,
            {"name": "Товар", "price": "-10.00", "category": self.cat_books.id},
        )
        self.assertEqual(res_neg_price.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", res_neg_price.data)

        res_no_name = self.client.post(
            self.list_url,
            {"name": "", "price": "100.00", "category": self.cat_books.id},
        )
        self.assertEqual(res_no_name.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res_no_name.data)


