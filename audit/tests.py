from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from audit.models import AuditLog
from customers.models import Customer
from transactions.models import Transaction

User = get_user_model()


class AuditLogAPITest(APITestCase):
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
            amount=Decimal("50000.00"),
            currency="NGN",
            transaction_type="transfer",
            status="pending",
        )

        self.audit = AuditLog.objects.create(
            transaction=self.transaction,
            action="RISK_ANALYSIS",
            actor="SYSTEM",
            details={
                "risk_score": 80,
            },
        )

    def test_list_audit_logs(self):
        url = reverse("audit-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_audit_log(self):
        url = reverse(
            "audit-detail",
            args=[self.audit.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["id"],
            str(self.audit.id),
        )

    def test_filter_by_action(self):
        url = reverse("audit-list")

        response = self.client.get(
            url,
            {
                "action": "RISK_ANALYSIS",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_transaction(self):
        url = reverse("audit-list")

        response = self.client.get(
            url,
            {
                "transaction": self.transaction.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_requires_authentication(self):
        self.client.credentials()

        url = reverse("audit-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
