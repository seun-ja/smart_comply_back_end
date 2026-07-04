from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(ReadOnlyModelViewSet):
    queryset = Alert.objects.select_related(
        "transaction",
        "transaction__customer",
    ).all()

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

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        alert.save(update_fields=["is_resolved"])

        return Response(
            AlertSerializer(alert).data,
            status=status.HTTP_200_OK,
        )
