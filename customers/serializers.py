from rest_framework import serializers

from transactions.models import Transaction

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    # TODO: Internal checks with AI
    is_high_risk = serializers.BooleanField(read_only=True)

    class Meta:
        model = Customer

        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "country",
            "is_high_risk",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "is_high_risk",
            "created_at",
            "updated_at",
        )

    def validate_email(self, value):
        return value.lower()


class CustomerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_high_risk",
        ]


class CustomerTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "reference",
            "amount",
            "currency",
            "status",
            "risk_score",
            "created_at",
        ]


class CustomerDetailSerializer(serializers.ModelSerializer):
    transactions = CustomerTransactionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "country",
            "is_high_risk",
            "transactions",
        ]
