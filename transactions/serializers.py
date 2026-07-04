from rest_framework import serializers

from alerts.serializers import AlertSerializer
from audit.serializers import AuditLogSerializer
from customers.models import Customer
from customers.serializers import CustomerSerializer

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source="customer",
        write_only=True,
    )

    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Transaction

        fields = [
            "id",
            "reference",
            "customer",
            "customer_id",
            "amount",
            "currency",
            "transaction_type",
            "status",
            "risk_score",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "reference",
            "risk_score",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):

        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")

        return value


class TransactionDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    alerts = AlertSerializer(many=True, read_only=True)
    audit_logs = AuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction

        fields = (
            "id",
            "amount",
            "currency",
            "transaction_type",
            "status",
            "risk_score",
            "created_at",
            "updated_at",
            "customer",
            "alerts",
            "audit_logs",
        )
