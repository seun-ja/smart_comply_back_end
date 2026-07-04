from django.db import models

from common.models import BaseModel


class Customer(BaseModel):
    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    country = models.CharField(
        max_length=2,
        db_index=True,
    )

    is_high_risk = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["country"]),
            models.Index(fields=["is_high_risk"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
