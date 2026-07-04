import json
import logging
import os

import django
import redis
from django.conf import settings

from rules.services import RiskAnalysisService

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

STREAM_NAME = "transaction-events"


def start_worker():
    logging.info("Worker started. Waiting for transaction events...")

    last_id = "0"

    while True:
        response = redis_client.xread(
            {STREAM_NAME: last_id},
            block=0,
        )

        for _, events in response:
            for event_id, data in events:
                last_id = event_id

                event = data["event"]

                payload = json.loads(data["payload"])

                if event == "transaction.created":
                    logging.info(f"Received event: {event}")
                    logging.info(f"Processing transaction: {payload['transaction_id']}")
                    logging.info("Risk analysis completed.")

                    RiskAnalysisService.process(payload["transaction_id"])


if __name__ == "__main__":
    start_worker()
