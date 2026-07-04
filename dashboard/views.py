from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.models import Alert
from customers.models import Customer
from transactions.models import Transaction


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "customers": Customer.objects.count(),
                "transactions": Transaction.objects.count(),
                "alerts": Alert.objects.count(),
                "high_risk": Customer.objects.filter(is_high_risk=True).count(),
                "recent_transactions": list(
                    Transaction.objects.order_by("-created_at")[:5].values(
                        "id",
                        "reference",
                        "amount",
                        "status",
                        "created_at",
                        "currency",
                    )
                ),
                "recent_alerts": list(
                    Alert.objects.order_by("-created_at")[:5].values(
                        "id",
                        "message",
                        "rule_name",
                        "severity",
                        "is_resolved",
                        "created_at",
                    )
                ),
            }
        )
