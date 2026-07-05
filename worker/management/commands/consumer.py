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


class Command(BaseCommand):
    help = "Starts the Redis stream consumer"

    def handle(self, *args, **options):

        logging.info("Worker started. Waiting for transaction events...")

        last_id = "0"

        while True:
            response = redis_client.xread(
                {STREAM_NAME: last_id},
                block=0,
            )

            for _, events in response:
                for event_id, data in events:
                    try:
                        last_id = event_id

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

                    except Exception:
                        logger.exception("Failed processing event %s", event_id)
