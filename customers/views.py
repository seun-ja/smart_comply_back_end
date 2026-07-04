from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()

    serializer_class = CustomerSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "country",
        "is_high_risk",
    ]

    search_fields = [
        "first_name",
        "last_name",
        "email",
    ]

    ordering_fields = [
        "created_at",
        "first_name",
    ]
