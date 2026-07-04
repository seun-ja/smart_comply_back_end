from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase

from alerts.models import AlertSeverity
from rules.high_amount import HighAmountRule


class HighAmountRuleTest(TestCase):
    def setUp(self):
        self.rule = HighAmountRule()

    def test_below_limit(self):
        """Test that a transaction below the limit does not trigger the rule."""
        mock_transaction = MagicMock()
        mock_transaction.amount = Decimal("9000.00")

        result = self.rule.evaluate(mock_transaction)

        self.assertFalse(result.triggered)
        self.assertEqual(result.score, 0)
        self.assertEqual(result.rule_name, "HighAmountRule")

    def test_at_limit(self):
        """Test that a transaction exactly at the limit does not trigger the rule."""
        mock_transaction = MagicMock()
        mock_transaction.amount = Decimal("10000.00")

        result = self.rule.evaluate(mock_transaction)

        self.assertFalse(result.triggered)
        self.assertEqual(result.score, 0)

    def test_above_limit(self):
        """Test that a transaction above the limit triggers the rule."""
        mock_transaction = MagicMock()
        mock_transaction.amount = Decimal("10000.01")

        result = self.rule.evaluate(mock_transaction)

        self.assertTrue(result.triggered)
        self.assertEqual(result.score, 40)
        self.assertEqual(result.severity, AlertSeverity.HIGH)
        self.assertIn("exceeds $10,000", result.message)
