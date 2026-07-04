from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):

    transaction_reference = serializers.CharField(
        source="transaction.reference",
        read_only=True,
    )

    customer = serializers.CharField(
        source="transaction.customer",
        read_only=True,
    )

    class Meta:
        model = AuditLog

        fields = [
            "id",
            "transaction",
            "transaction_reference",
            "customer",
            "action",
            "actor",
            "details",
            "created_at",
        ]

        read_only_fields = fields