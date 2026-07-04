from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related(
        "transaction",
        "transaction__customer",
    ).all()

    serializer_class = AuditLogSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "action",
        "actor",
    ]

    search_fields = [
        "transaction__reference",
        "transaction__customer__first_name",
        "transaction__customer__last_name",
    ]

    ordering_fields = [
        "created_at",
        "action",
    ]
