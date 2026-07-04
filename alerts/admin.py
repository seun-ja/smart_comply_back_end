from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "rule_name",
        "severity",
        "is_resolved",
        "created_at",
    )

    list_filter = (
        "severity",
        "is_resolved",
    )

    search_fields = (
        "rule_name",
        "transaction__reference",
    )
