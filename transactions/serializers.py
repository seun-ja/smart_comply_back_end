from rest_framework import serializers

from customers.models import Customer
from customers.serializers import CustomerSummarySerializer

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
    customer = CustomerSummarySerializer(read_only=True)
    alerts = serializers.SerializerMethodField()
    audit_logs = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def get_alerts(self, obj):
        from alerts.serializers import AlertSerializer

        return AlertSerializer(
            obj.alerts.all(),
            many=True,
        ).data

    def get_audit_logs(self, obj):
        from audit.serializers import AuditLogSerializer

        return AuditLogSerializer(
            obj.audit_logs.all(),
            many=True,
        ).data
