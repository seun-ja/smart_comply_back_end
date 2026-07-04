from django.db import models

from common.models import BaseModel
from transactions.models import Transaction


class AuditAction(models.TextChoices):
    TRANSACTION_CREATED = "TRANSACTION_CREATED", "Transaction Created"
    RISK_ANALYSIS = "RISK_ANALYSIS", "Risk Analysis"
    STATUS_UPDATED = "STATUS_UPDATED", "Status Updated"


class AuditLog(BaseModel):

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=50,
        choices=AuditAction.choices,
    )

    actor = models.CharField(
        max_length=100,
        default="SYSTEM",
    )

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction.reference} - {self.action}"