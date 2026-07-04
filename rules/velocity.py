from datetime import timedelta

from django.utils import timezone

from alerts.models import AlertSeverity

from transactions.models import Transaction

from .base import Rule
from .base import RuleResult


class VelocityRule(Rule):

    def evaluate(self, transaction):

        last_hour = timezone.now() - timedelta(hours=1)

        count = Transaction.objects.filter(
            customer=transaction.customer,
            created_at__gte=last_hour,
        ).count()

        if count <= 5:

            return RuleResult(
                False,
                0,
                "",
                "",
                self.__class__.__name__,
            )

        return RuleResult(
            True,
            30,
            AlertSeverity.MEDIUM,
            "More than five transactions in one hour.",
            self.__class__.__name__,
        )