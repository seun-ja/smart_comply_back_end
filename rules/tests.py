from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from alerts.models import AlertSeverity
from rules.base import RuleResult
from rules.black_list_country import BlacklistedCountryRule
from rules.engine import evaluate_transaction
from rules.high_amount import HighAmountRule
from rules.high_risk_customer import HighRiskCustomerRule
from rules.velocity import VelocityRule


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

    def test_negative_amount(self):
        """Test that a negative amount does not trigger the rule."""
        mock_transaction = MagicMock()
        mock_transaction.amount = Decimal("-10000.00")
        result = self.rule.evaluate(mock_transaction)
        self.assertFalse(result.triggered)


class BlacklistedCountryRuleTest(TestCase):
    def setUp(self):
        self.rule = BlacklistedCountryRule()

    def test_blacklisted_country_blocked(self):
        """Test that a transaction from a blacklisted country triggers the rule."""
        mock_transaction = MagicMock()
        mock_transaction.customer.country = "KP"
        result = self.rule.evaluate(mock_transaction)
        self.assertTrue(result.triggered)
        self.assertEqual(result.score, 80)
        self.assertEqual(result.severity, AlertSeverity.HIGH)
        self.assertEqual(result.message, "Blacklisted country.")

    def test_blacklisted_country_allowed(self):
        """Test that a transaction from a non-blacklisted country does not trigger the rule."""
        mock_transaction = MagicMock()
        mock_transaction.customer.country = "US"
        result = self.rule.evaluate(mock_transaction)
        self.assertFalse(result.triggered)
        self.assertEqual(result.score, 0)
        self.assertEqual(result.message, "")

    def test_empty_country(self):
        """Test that an empty country code does not trigger the rule."""
        mock_transaction = MagicMock()
        mock_transaction.customer.country = ""
        result = self.rule.evaluate(mock_transaction)
        self.assertFalse(result.triggered)


class HighRiskCustomerRuleTest(TestCase):
    def setUp(self):
        self.rule = HighRiskCustomerRule()

    def test_high_risk_customer_triggered(self):
        """Test that a transaction for a high-risk customer triggers the rule."""
        mock_transaction = MagicMock()
        mock_transaction.customer.is_high_risk = True
        result = self.rule.evaluate(mock_transaction)
        self.assertTrue(result.triggered)
        self.assertEqual(result.score, 50)
        self.assertEqual(result.severity, AlertSeverity.HIGH)
        self.assertEqual(result.message, "High risk customer.")

    def test_high_risk_customer_not_triggered(self):
        """Test that a transaction for a normal customer does not trigger the rule."""
        mock_transaction = MagicMock()
        mock_transaction.customer.is_high_risk = False
        result = self.rule.evaluate(mock_transaction)
        self.assertFalse(result.triggered)
        self.assertEqual(result.score, 0)
        self.assertEqual(result.message, "")


class VelocityRuleTest(TestCase):
    def setUp(self):
        self.rule = VelocityRule()

    def test_velocity_rule_no_trigger(self):
        """Test that VelocityRule does not trigger when count <= 5."""
        mock_transaction = MagicMock()
        with patch("transactions.models.Transaction.objects.filter") as mock_filter:
            mock_query = MagicMock()
            mock_query.count.return_value = 1
            mock_filter.return_value = mock_query

            result = self.rule.evaluate(mock_transaction)
            self.assertFalse(result.triggered)
            self.assertEqual(result.score, 0)

    def test_velocity_rule_triggered(self):
        """Test that VelocityRule triggers when count > 5."""
        mock_transaction = MagicMock()
        with patch("transactions.models.Transaction.objects.filter") as mock_filter:
            mock_query = MagicMock()
            mock_query.count.return_value = 6
            mock_filter.return_value = mock_query

            result = self.rule.evaluate(mock_transaction)
            self.assertTrue(result.triggered)
            self.assertEqual(result.score, 30)
            self.assertEqual(result.severity, AlertSeverity.MEDIUM)
            self.assertIn("More than five transactions in one hour.", result.message)

    def test_velocity_rule_zero_count(self):
        """Test that VelocityRule does not trigger when count is 0."""
        mock_transaction = MagicMock()
        with patch("transactions.models.Transaction.objects.filter") as mock_filter:
            mock_query = MagicMock()
            mock_query.count.return_value = 0
            mock_filter.return_value = mock_query

            result = self.rule.evaluate(mock_transaction)
            self.assertFalse(result.triggered)
            self.assertEqual(result.score, 0)


class EngineTest(TestCase):
    @patch("rules.engine.discover_rules")
    def test_evaluate_transaction_no_rules(self, mock_discover):
        """Test that when no rules are registered, the score is 0 and no results are returned."""
        mock_discover.return_value = []
        mock_transaction = MagicMock()

        results, score = evaluate_transaction(mock_transaction)

        self.assertEqual(len(results), 0)
        self.assertEqual(score, 0)

    @patch("rules.engine.discover_rules")
    def test_evaluate_transaction_multiple_triggered(self, mock_discover):
        """Test that multiple rules can be triggered simultaneously
        and their scores are summed correctly."""

        # Mocking rule classes
        class MockRule1(object):
            def evaluate(self, transaction):
                return RuleResult(True, 50, "HIGH", "Rule 1", "MockRule1")

        class MockRule2(object):
            def evaluate(self, transaction):
                return RuleResult(True, 30, "MEDIUM", "Rule 2", "MockRule2")

        mock_discover.return_value = [MockRule1, MockRule2]
        mock_transaction = MagicMock()

        results, score = evaluate_transaction(mock_transaction)

        self.assertEqual(len(results), 2)
        self.assertEqual(score, 80)

    @patch("rules.engine.discover_rules")
    def test_evaluate_transaction_with_error(self, mock_discover):
        """Test that if a single rule fails (raises an exception),
        the engine catches it, logs the error, and continues to other rules."""

        class FailingRule:
            def evaluate(self, transaction):
                raise ValueError("Simulated Error")

        class WorkingRule:
            def evaluate(self, transaction):
                return RuleResult(False, 0, "", "", "WorkingRule")

        mock_discover.return_value = [FailingRule, WorkingRule]
        mock_transaction = MagicMock()
        mock_transaction.id = 123

        with self.assertLogs("rules.engine", level="ERROR") as cm:
            results, score = evaluate_transaction(mock_transaction)

            # Ensure only the working rule's result is present
            self.assertEqual(len(results), 1)
            self.assertEqual(score, 0)
            # Verify error was logged
            self.assertTrue(
                any("Rule FailingRule failed" in output for output in cm.output)
            )
