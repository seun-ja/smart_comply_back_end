from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(ReadOnlyModelViewSet):

    queryset = (
        Alert.objects
        .select_related(
            "transaction",
            "transaction__customer",
        )
        .all()
    )

    serializer_class = AlertSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "severity",
        "is_resolved",
    ]

    search_fields = [
        "rule_name",
        "message",
        "transaction__reference",
        "transaction__customer__first_name",
        "transaction__customer__last_name",
    ]

    ordering_fields = [
        "created_at",
        "severity",
    ]