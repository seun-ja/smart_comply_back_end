from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from alerts.models import Alert
from customers.models import Customer
from transactions.models import Transaction

User = get_user_model()


class DashboardAPITest(APITestCase):
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
            is_high_risk=True,
        )

        self.transaction = Transaction.objects.create(
            customer=self.customer,
            amount=Decimal("250000"),
            currency="NGN",
            transaction_type="transfer",
            status="pending",
            risk_score=90,
        )

        Alert.objects.create(
            transaction=self.transaction,
            rule_name="HighAmountRule",
            severity="HIGH",
            message="High amount transaction.",
        )

    def test_dashboard_returns_statistics(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data

        self.assertEqual(data["customers"], 1)
        self.assertEqual(data["transactions"], 1)
        self.assertEqual(data["alerts"], 1)
        self.assertEqual(data["high_risk"], 1)

    def test_dashboard_contains_recent_transactions(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["recent_transactions"]),
            1,
        )

    def test_dashboard_contains_recent_alerts(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["recent_alerts"]),
            1,
        )

    def test_dashboard_requires_authentication(self):
        self.client.credentials()

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
