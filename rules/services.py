from alerts.models import Alert
from audit.models import (
    AuditAction,
    AuditLog,
)
from transactions.models import Transaction

from .engine import RuleEngine


class RiskAnalysisService:
    @staticmethod
    def process(transaction_id):

        transaction = Transaction.objects.select_related("customer").get(
            id=transaction_id
        )

        engine = RuleEngine()

        results, score = engine.evaluate(transaction)

        transaction.risk_score = score

        transaction.save(
            update_fields=[
                "risk_score",
            ]
        )

        customer = transaction.customer

        if score >= 80 and not customer.is_high_risk:
            customer.is_high_risk = True
            customer.save(update_fields=["is_high_risk"])

        for result in results:
            Alert.objects.create(
                transaction=transaction,
                rule_name=result.rule_name,
                severity=result.severity,
                message=result.message,
            )

        AuditLog.objects.create(
            transaction=transaction,
            action=AuditAction.RISK_ANALYSIS,
            actor="SYSTEM",
            details={
                "risk_score": score,
                "rules": [r.rule_name for r in results],
            },
        )
