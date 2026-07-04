import logging

from transactions.models import Transaction

from .registry import discover_rules


def evaluate_transaction(transaction: Transaction):
    """
    Executes all registered compliance rules against a transaction.

    Returns:
        tuple[list[RuleResult], int]
    """

    results = []

    for rule_cls in discover_rules():
        rule = rule_cls()

        try:
            result = rule.evaluate(transaction)
            results.append(result)

        except Exception:
            logging.exception(
                "Rule %s failed while evaluating transaction %s",
                rule_cls.__name__,
                transaction.id,
            )

    score = sum(result.score for result in results)

    return results, score
