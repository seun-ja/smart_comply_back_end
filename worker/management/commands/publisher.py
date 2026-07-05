import json
import logging

import redis
from django.conf import settings

from transactions.models import Transaction

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


STREAM_NAME = getattr(
    settings,
    "TRANSACTION_STREAM_NAME",
    "transaction-events",
)


class EventPublisher:
    @staticmethod
    def transaction_created(transaction: Transaction):
        logger = logging.getLogger(__name__)

        try:
            redis_client.xadd(
                STREAM_NAME,
                {
                    "event": "transaction.created",
                    "payload": json.dumps(
                        {
                            "transaction_id": str(transaction.id),
                        }
                    ),
                },
            )
        except redis.RedisError:
            logger.exception(
                "Failed to publish transaction.created for %s",
                transaction.id,
            )
