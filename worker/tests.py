import json
import uuid
from unittest.mock import MagicMock, patch

import redis
from django.test import TestCase

from worker.management.commands.consumer import Command
from worker.management.commands.publisher import EventPublisher


class TestWorker(TestCase):
    def setUp(self):
        self.mock_transaction = MagicMock()
        self.mock_transaction.id = str(uuid.uuid4())
        self.mock_transaction.reference = "TXN-TEST"

    @patch("worker.management.commands.publisher.redis_client")
    def test_publish_transaction_created_success(self, mock_redis):
        """Test that transaction created event is published correctly to redis."""
        EventPublisher.transaction_created(self.mock_transaction)

        mock_redis.xadd.assert_called_once()
        args, kwargs = mock_redis.xadd.call_args

        messages = args[1]

        self.assertEqual(messages["event"], "transaction.created")
        payload = json.loads(messages["payload"])
        self.assertEqual(payload["transaction_id"], self.mock_transaction.id)

    @patch("worker.management.commands.publisher.redis_client")
    def test_publish_transaction_created_failure(self, mock_redis):
        """Test that transaction created event handles redis errors gracefully."""
        mock_redis.xadd.side_effect = redis.RedisError("Connection refused")

        # Should not raise exception but log it
        EventPublisher.transaction_created(self.mock_transaction)

        mock_redis.xadd.assert_called_once()

    @patch("worker.management.commands.consumer.redis_client")
    @patch("rules.services.RiskAnalysisService.process")
    def test_consumer_processes_event(self, mock_process, mock_redis):
        """Test that the consumer correctly processes a 'transaction.created' event."""
        mock_id = str(uuid.uuid4())
        mock_event = {
            "event": "transaction.created",
            "payload": json.dumps({"transaction_id": mock_id}),
        }

        mock_redis.xreadgroup.side_effect = [
            [("consumer_1", [("event_id_1", mock_event)])],
            Exception("Break Loop"),
        ]

        mock_redis.xack.return_value = True

        with self.assertRaises(Exception) as cm:
            command = Command()
            command.handle()

        self.assertEqual(str(cm.exception), "Break Loop")

        mock_process.assert_called_once_with(mock_id)
        mock_redis.xack.assert_called_with(
            "transaction-events", "transactions_group", "event_id_1"
        )
