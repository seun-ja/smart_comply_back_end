from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Transaction
from .serializers import TransactionSerializer
from .services import TransactionService


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all().order_by("-created_at")

    serializer_class = TransactionSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "status",
        "currency",
        "transaction_type",
    ]

    search_fields = [
        "reference",
        "customer__first_name",
        "customer__last_name",
        "customer__email",
    ]

    ordering_fields = [
        "amount",
        "created_at",
        "risk_score",
    ]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        transaction = TransactionService.create(serializer.validated_data)

        response = self.get_serializer(transaction)

        return Response(
            response.data,
            status=status.HTTP_201_CREATED,
        )

    def perform_update(
        self,
        serializer,
    ):

        TransactionService.update(
            serializer.instance,
            serializer.validated_data,
        )

    def get_queryset(self):
        queryset = super().get_queryset()

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset
