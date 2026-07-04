import logging

from django.db import transaction as db_transaction

from worker.publisher import EventPublisher

from .models import Transaction


class TransactionService:
    @staticmethod
    @db_transaction.atomic
    def create(validated_data):

        logging.info(f"Creating transaction with data: {validated_data}")
        transaction = Transaction.objects.create(**validated_data)

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
