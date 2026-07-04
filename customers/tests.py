from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer

User = get_user_model()


class CustomerAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="password123",
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": "admin",
                "password": "password123",
            },
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

        self.customer = Customer.objects.create(
            first_name="Joshua",
            last_name="Aminu",
            email="joshua@example.com",
            country="NG",
        )

    def test_list_customers(self):
        response = self.client.get(reverse("customers-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_customer(self):
        response = self.client.get(reverse("customers-detail", args=[self.customer.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["email"],
            "joshua@example.com",
        )

    def test_create_customer(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "country": "US",
        }

        response = self.client.post(
            reverse("customers-list"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Customer.objects.count(), 2)

    def test_update_customer(self):
        response = self.client.patch(
            reverse("customers-detail", args=[self.customer.id]),
            {
                "country": "GB",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.customer.refresh_from_db()

        self.assertEqual(
            self.customer.country,
            "GB",
        )

    def test_delete_customer(self):
        response = self.client.delete(
            reverse("customers-detail", args=[self.customer.id])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertEqual(Customer.objects.count(), 0)

    def test_search_customer(self):
        response = self.client.get(
            reverse("customers-list"),
            {
                "search": "Joshua",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_requires_authentication(self):
        self.client.credentials()

        response = self.client.get(reverse("customers-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
