import logging

from django.db import transaction as db_transaction

from alerts.models import Alert
from audit.models import AuditAction, AuditLog
from rules.engine import evaluate_transaction
from worker.publisher import EventPublisher

from .models import Transaction


class TransactionService:
    @staticmethod
    @db_transaction.atomic
    def create(validated_data):
        logging.info(f"Creating transaction with data: {validated_data}")
        transaction = Transaction.objects.create(**validated_data)

        # Run all compliance rules
        results = evaluate_transaction(transaction)

        # Calculate overall risk score
        score = sum(result.score for result in results)

        transaction.risk_score = score
        transaction.save(update_fields=["risk_score"])

        # Persist alerts
        for result in results:
            if result.triggered:
                Alert.objects.create(
                    transaction=transaction,
                    rule_name=result.rule_name,
                    severity=result.severity,
                    message=result.message,
                )

        # Automatically classify customer as high risk
        customer = transaction.customer

        if not customer.is_high_risk and score >= 80:
            customer.is_high_risk = True
            customer.save(update_fields=["is_high_risk"])

        # Create audit record
        AuditLog.objects.create(
            transaction=transaction,
            action=AuditAction.RISK_ANALYSIS,
            actor="SYSTEM",
            details={
                "risk_score": score,
                "rules": [result.rule_name for result in results if result.triggered],
            },
        )

        # Publish Kafka event
        EventPublisher.transaction_created(transaction)

        return transaction

    @staticmethod
    @db_transaction.atomic
    def update(instance, validated_data):
        logging.info(f"Updating transaction instance {instance.id}")

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance
