import uuid

from django.db import models

from common.models import BaseModel
from customers.models import Customer


class TransactionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class TransactionType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Deposit"
    WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
    TRANSFER = "TRANSFER", "Transfer"


class Transaction(BaseModel):

    reference = models.CharField(
        max_length=40,
        unique=True,
        db_index=True,
        editable=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        db_index=True,
    )

    risk_score = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["status"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):

        if not self.reference:
            self.reference = (
                f"TXN-{uuid.uuid4().hex[:12].upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference