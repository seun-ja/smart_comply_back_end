from django.db import models

from common.models import BaseModel
from transactions.models import Transaction


class AlertSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class Alert(BaseModel):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="alerts",
    )

    rule_name = models.CharField(max_length=100)

    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
    )

    message = models.TextField()

    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rule_name} - {self.transaction.reference}"