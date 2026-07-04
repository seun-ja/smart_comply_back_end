from rest_framework import serializers

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
            "created_at",
            "updated_at",
        )

    def validate_email(self, value):
        return value.lower()
