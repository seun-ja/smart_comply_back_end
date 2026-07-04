from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from alerts.models import Alert
from customers.models import Customer
from transactions.models import Transaction

User = get_user_model()


class AlertAPITest(APITestCase):
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
            email="test@example.com",
            country="NG",
        )

        self.transaction = Transaction.objects.create(
            customer=self.customer,
            amount=Decimal("250000.00"),
            currency="NGN",
            transaction_type="transfer",
            status="pending",
        )

        self.alert = Alert.objects.create(
            transaction=self.transaction,
            rule_name="HighAmountRule",
            severity="HIGH",
            message="High amount transaction.",
        )

    def test_list_alerts(self):
        url = reverse("alerts-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_alert(self):
        url = reverse("alerts-detail", args=[self.alert.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.alert.id))

    def test_filter_by_severity(self):
        url = reverse("alerts-list")

        response = self.client.get(
            url,
            {
                "severity": "HIGH",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_mark_alert_resolved(self):
        url = reverse("alerts-resolve", args=[self.alert.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.alert.refresh_from_db()

        self.assertTrue(self.alert.is_resolved)

    def test_requires_authentication(self):
        self.client.credentials()

        url = reverse("alerts-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
