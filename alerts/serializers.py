from rest_framework import serializers

from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    transaction_reference = serializers.CharField(
        source="transaction.reference",
        read_only=True,
    )

    customer = serializers.CharField(
        source="transaction.customer",
        read_only=True,
    )

    class Meta:
        model = Alert

        fields = [
            "id",
            "transaction",
            "transaction_reference",
            "customer",
            "rule_name",
            "severity",
            "message",
            "is_resolved",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]
