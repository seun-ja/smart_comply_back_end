from .registry import discover_rules


class RuleEngine:

    def __init__(self):

        self.rules = discover_rules()

    def evaluate(
        self,
        transaction,
    ):

        alerts = []

        score = 0

        for rule in self.rules:

            result = rule.evaluate(transaction)

            if not result.triggered:
                continue

            alerts.append(result)

            score += result.score

        return alerts, score