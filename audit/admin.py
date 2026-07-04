from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "transaction",
        "action",
        "actor",
        "created_at",
    )

    list_filter = (
        "action",
        "actor",
    )

    search_fields = (
        "transaction__reference",
    )