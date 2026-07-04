from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "country",
        "is_high_risk",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
    )

    list_filter = (
        "country",
        "is_high_risk",
    )