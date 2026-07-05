import json
import logging

import redis
from django.conf import settings
from django.core.management.base import BaseCommand

from rules.services import RiskAnalysisService

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

STREAM_NAME = "transaction-events"
GROUP_NAME = "transactions_group"
CONSUMER_NAME = "worker_1"


class Command(BaseCommand):
    help = "Starts the Redis stream consumer"

    def handle(self, *args, **options):

        logging.info("Worker started. Waiting for transaction events...")

        # Ensure the consumer group exists
        try:
            redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id=">", mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "Already exists" not in str(e):
                raise

        while True:
            response = redis_client.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: ">"},
                block=0,
            )

            for _, events in response:
                for event_id, data in events:
                    try:
                        event = data["event"]
                        payload = json.loads(data["payload"])

                        if event == "transaction.created":
                            logger.info(
                                "Processing transaction %s",
                                payload["transaction_id"],
                            )

                            RiskAnalysisService.process(payload["transaction_id"])

                            logger.info(
                                "Completed transaction %s",
                                payload["transaction_id"],
                            )

                        # Acknowledge the message after successful processing
                        redis_client.xack(STREAM_NAME, GROUP_NAME, event_id)

                    except Exception:
                        logger.exception("Failed processing event %s", event_id)
