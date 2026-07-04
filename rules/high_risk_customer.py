from alerts.models import AlertSeverity

from .base import Rule
from .base import RuleResult


class HighRiskCustomerRule(Rule):

    def evaluate(self, transaction):

        if not transaction.customer.is_high_risk:

            return RuleResult(
                False,
                0,
                "",
                "",
                self.__class__.__name__,
            )

        return RuleResult(
            True,
            50,
            AlertSeverity.HIGH,
            "High risk customer.",
            self.__class__.__name__,
        )