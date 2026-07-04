from alerts.models import AlertSeverity

from .base import Rule, RuleResult


class HighAmountRule(Rule):
    LIMIT = 10000

    def evaluate(self, transaction):

        if transaction.amount <= self.LIMIT:
            return RuleResult(
                triggered=False,
                score=0,
                severity="",
                message="",
                rule_name=self.__class__.__name__,
            )

        return RuleResult(
            triggered=True,
            score=40,
            severity=AlertSeverity.HIGH,
            message="Transaction exceeds $10,000.",
            rule_name=self.__class__.__name__,
        )
