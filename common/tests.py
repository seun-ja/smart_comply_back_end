from django.test import SimpleTestCase

from common.constants import (
    TransactionStatus,
    TransactionType,
)


class TransactionStatusTests(SimpleTestCase):
    def test_pending_status(self):
        self.assertEqual(
            TransactionStatus.PENDING,
            "pending",
        )

    def test_approved_status(self):
        self.assertEqual(
            TransactionStatus.APPROVED,
            "approved",
        )

    def test_rejected_status(self):
        self.assertEqual(
            TransactionStatus.REJECTED,
            "rejected",
        )

    def test_status_choices(self):
        self.assertIn(
            (
                TransactionStatus.PENDING,
                "Pending",
            ),
            TransactionStatus.CHOICES,
        )


class TransactionTypeTests(SimpleTestCase):
    def test_deposit_type(self):
        self.assertEqual(
            TransactionType.DEPOSIT,
            "deposit",
        )

    def test_withdrawal_type(self):
        self.assertEqual(
            TransactionType.WITHDRAWAL,
            "withdrawal",
        )

    def test_transfer_type(self):
        self.assertEqual(
            TransactionType.TRANSFER,
            "transfer",
        )

    def test_type_choices(self):
        self.assertIn(
            (
                TransactionType.TRANSFER,
                "Transfer",
            ),
            TransactionType.CHOICES,
        )
