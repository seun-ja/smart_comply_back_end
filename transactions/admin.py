from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "customer",
        "amount",
        "currency",
        "transaction_type",
        "status",
        "risk_score",
        "created_at",
    )

    search_fields = (
        "reference",
        "customer__first_name",
        "customer__last_name",
    )

    list_filter = (
        "status",
        "currency",
        "transaction_type",
    )
