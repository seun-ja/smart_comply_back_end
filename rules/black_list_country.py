from alerts.models import AlertSeverity

from .base import Rule, RuleResult

BLACKLIST = {
    "KP",
    "IR",
    "SY",
}


class BlacklistedCountryRule(Rule):
    def evaluate(self, transaction):

        if transaction.customer.country not in BLACKLIST:
            return RuleResult(
                False,
                0,
                "",
                "",
                self.__class__.__name__,
            )

        return RuleResult(
            True,
            80,
            AlertSeverity.HIGH,
            "Blacklisted country.",
            self.__class__.__name__,
        )
