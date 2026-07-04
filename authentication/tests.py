from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.username = "admin"
        self.password = "password123"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.username,
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_token(self):
        login = self.client.post(
            reverse("login"),
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        response = self.client.post(
            reverse("refresh"),
            {
                "refresh": login.data["refresh"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_invalid_token(self):
        response = self.client.post(
            reverse("refresh"),
            {
                "refresh": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_protected_endpoint_requires_authentication(self):
        response = self.client.get(reverse("customers-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_protected_endpoint_with_token(self):
        login = self.client.post(
            reverse("login"),
            {
                "username": self.username,
                "password": self.password,
            },
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.get(reverse("customers-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
