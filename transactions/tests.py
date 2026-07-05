from decimal import Decimal
from unittest.mock import patch

import pytest

from customers.models import Customer
from rules.base import RuleResult

from .models import Transaction, TransactionStatus, TransactionType
from .services import TransactionService

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestTransactionService:
    def make_customer(self):
        return Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            country="US",
        )

    def make_payload(self, customer, amount=Decimal("100.00")):
        return {
            "amount": amount,
            "currency": "USD",
            "transaction_type": TransactionType.DEPOSIT.value,
            "status": TransactionStatus.PENDING.value,
            "customer": customer,
        }

    @patch("transactions.services.EventPublisher.transaction_created")
    @patch("transactions.services.AuditLog.objects.create")
    @patch("transactions.services.Alert.objects.create")
    @patch("transactions.services.evaluate_transaction")
    def test_create_transaction_low_risk(
        self,
        mock_evaluate,
        mock_alert_create,
        mock_audit_create,
        mock_publish,
    ):
        customer = self.make_customer()

        mock_evaluate.return_value = (
            [],
            0,
        )

        transaction = TransactionService.create(self.make_payload(customer))

        customer.refresh_from_db()

        assert transaction.pk is not None
        assert transaction.risk_score == 0
        assert customer.is_high_risk is False

        mock_evaluate.assert_called_once_with(transaction)

        mock_alert_create.assert_not_called()

        mock_audit_create.assert_called_once()

        mock_publish.assert_called_once_with(transaction)

    @patch("transactions.services.EventPublisher.transaction_created")
    @patch("transactions.services.AuditLog.objects.create")
    @patch("transactions.services.Alert.objects.create")
    @patch("transactions.services.evaluate_transaction")
    def test_create_transaction_high_risk(
        self,
        mock_evaluate,
        mock_alert_create,
        mock_audit_create,
        mock_publish,
    ):
        customer = self.make_customer()

        results = [
            RuleResult(
                triggered=True,
                score=85,
                severity="HIGH",
                message="High amount transaction",
                rule_name="HighAmountRule",
            )
        ]

        mock_evaluate.return_value = (
            results,
            85,
        )

        transaction = TransactionService.create(
            self.make_payload(customer, Decimal("10000"))
        )

        customer.refresh_from_db()

        assert transaction.risk_score == 85
        assert customer.is_high_risk is True

        mock_alert_create.assert_called_once_with(
            transaction=transaction,
            rule_name="HighAmountRule",
            severity="HIGH",
            message="High amount transaction",
        )

        mock_audit_create.assert_called_once()

        mock_publish.assert_called_once_with(transaction)

    @patch("transactions.services.EventPublisher.transaction_created")
    @patch("transactions.services.AuditLog.objects.create")
    @patch("transactions.services.Alert.objects.create")
    @patch("transactions.services.evaluate_transaction")
    def test_only_triggered_rules_generate_alerts(
        self,
        mock_evaluate,
        mock_alert_create,
        mock_audit_create,
        mock_publish,
    ):
        customer = self.make_customer()

        results = [
            RuleResult(
                triggered=False,
                score=0,
                severity="",
                message="",
                rule_name="RuleOne",
            ),
            RuleResult(
                triggered=True,
                score=20,
                severity="LOW",
                message="Triggered",
                rule_name="RuleTwo",
            ),
        ]

        mock_evaluate.return_value = (
            results,
            20,
        )

        transaction = TransactionService.create(self.make_payload(customer))

        assert transaction.risk_score == 20

        mock_alert_create.assert_called_once()

        mock_alert_create.assert_called_with(
            transaction=transaction,
            rule_name="RuleTwo",
            severity="LOW",
            message="Triggered",
        )

        mock_audit_create.assert_called()

        mock_publish.assert_called_once_with(transaction)

    @patch("transactions.services.EventPublisher.transaction_created")
    @patch("transactions.services.AuditLog.objects.create")
    @patch("transactions.services.Alert.objects.create")
    @patch("transactions.services.evaluate_transaction")
    def test_existing_high_risk_customer_not_updated_again(
        self,
        mock_evaluate,
        mock_alert_create,
        mock_audit_create,
        mock_publish,
    ):
        customer = self.make_customer()
        customer.is_high_risk = True
        customer.save()

        results = [
            RuleResult(
                triggered=True,
                score=95,
                severity="HIGH",
                message="Still risky",
                rule_name="Rule",
            )
        ]

        mock_evaluate.return_value = (results, 95)

        with patch.object(customer, "save") as mock_save:
            TransactionService.create(self.make_payload(customer, Decimal("15000")))

            mock_save.assert_not_called()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("status", TransactionStatus.APPROVED.value),
            ("risk_score", 30),
            ("currency", "EUR"),
        ],
    )
    def test_update_transaction(self, field, value):
        customer = self.make_customer()

        transaction = Transaction.objects.create(
            amount=Decimal("100"),
            currency="USD",
            transaction_type=TransactionType.DEPOSIT.value,
            status=TransactionStatus.PENDING.value,
            customer=customer,
        )

        updated = TransactionService.update(
            transaction,
            {field: value},
        )

        updated.refresh_from_db()

        assert getattr(updated, field) == value


@pytest.fixture
def customer():
    return Customer.objects.create(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        country="US",
    )


@pytest.fixture
def transaction(customer):
    return Transaction.objects.create(
        customer=customer,
        amount=Decimal("100.00"),
        currency="USD",
        transaction_type=TransactionType.DEPOSIT,
        status=TransactionStatus.PENDING,
    )


@patch("transactions.services.EventPublisher.transaction_created")
@patch("transactions.services.AuditLog.objects.create")
@patch("transactions.services.Alert.objects.create")
@patch("transactions.services.evaluate_transaction")
def test_create_transaction_low_risk(
    mock_evaluate,
    mock_alert,
    mock_audit,
    mock_publish,
    customer,
):
    mock_evaluate.return_value = (
        [],
        0,
    )

    tx = TransactionService.create(
        {
            "customer": customer,
            "amount": Decimal("100"),
            "currency": "USD",
            "transaction_type": TransactionType.DEPOSIT,
            "status": TransactionStatus.PENDING,
        }
    )

    customer.refresh_from_db()

    assert tx.risk_score == 0
    assert customer.is_high_risk is False

    mock_alert.assert_not_called()

    mock_audit.assert_called_once()

    mock_publish.assert_called_once_with(tx)


@patch("transactions.services.EventPublisher.transaction_created")
@patch("transactions.services.AuditLog.objects.create")
@patch("transactions.services.Alert.objects.create")
@patch("transactions.services.evaluate_transaction")
def test_create_transaction_high_risk(
    mock_evaluate,
    mock_alert,
    mock_audit,
    mock_publish,
    customer,
):
    results = [
        RuleResult(
            triggered=True,
            score=90,
            severity="HIGH",
            message="Large transfer",
            rule_name="HighAmountRule",
        )
    ]

    mock_evaluate.return_value = (results, 90)

    tx = TransactionService.create(
        {
            "customer": customer,
            "amount": Decimal("15000"),
            "currency": "USD",
            "transaction_type": TransactionType.TRANSFER,
            "status": TransactionStatus.PENDING,
        }
    )

    customer.refresh_from_db()

    assert tx.risk_score == 90
    assert customer.is_high_risk is True

    mock_alert.assert_called_once_with(
        transaction=tx,
        rule_name="HighAmountRule",
        severity="HIGH",
        message="Large transfer",
    )

    mock_audit.assert_called_once()

    mock_publish.assert_called_once_with(tx)


@patch("transactions.services.EventPublisher.transaction_created")
@patch("transactions.services.AuditLog.objects.create")
@patch("transactions.services.Alert.objects.create")
@patch("transactions.services.evaluate_transaction")
def test_existing_high_risk_customer_not_updated(
    mock_evaluate,
    mock_alert,
    mock_audit,
    mock_publish,
):
    customer = Customer.objects.create(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        country="US",
        is_high_risk=True,
    )

    results = [
        RuleResult(
            triggered=True,
            score=95,
            severity="HIGH",
            message="Risk detected",
            rule_name="RuleA",
        )
    ]

    mock_evaluate.return_value = (results, 95)

    tx = TransactionService.create(
        {
            "customer": customer,
            "amount": Decimal("20000"),
            "currency": "USD",
            "transaction_type": TransactionType.TRANSFER,
            "status": TransactionStatus.PENDING,
        }
    )

    customer.refresh_from_db()

    assert customer.is_high_risk is True
    assert tx.risk_score == 95

    mock_alert.assert_called_once()
    mock_publish.assert_called_once()


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", TransactionStatus.APPROVED),
        ("risk_score", 40),
        ("currency", "EUR"),
    ],
)
def test_update_transaction(field, value, transaction):
    updated = TransactionService.update(
        transaction,
        {field: value},
    )

    updated.refresh_from_db()

    assert getattr(updated, field) == value


def test_update_multiple_fields(transaction):
    updated = TransactionService.update(
        transaction,
        {
            "status": TransactionStatus.REJECTED,
            "risk_score": 85,
            "currency": "EUR",
        },
    )

    updated.refresh_from_db()

    assert updated.status == TransactionStatus.REJECTED
    assert updated.risk_score == 85
    assert updated.currency == "EUR"


@patch("transactions.services.EventPublisher.transaction_created")
@patch("transactions.services.AuditLog.objects.create")
@patch("transactions.services.Alert.objects.create")
@patch("transactions.services.evaluate_transaction")
def test_multiple_rules_accumulate_score(
    mock_evaluate,
    mock_alert,
    mock_audit,
    mock_publish,
    customer,
):
    results = [
        RuleResult(True, 30, "MEDIUM", "Rule A", "RuleA"),
        RuleResult(True, 60, "HIGH", "Rule B", "RuleB"),
        RuleResult(False, 0, "", "", "RuleC"),
    ]

    mock_evaluate.return_value = (results, 90)

    tx = TransactionService.create(
        {
            "customer": customer,
            "amount": Decimal("5000"),
            "currency": "USD",
            "transaction_type": TransactionType.TRANSFER,
            "status": TransactionStatus.PENDING,
        }
    )

    customer.refresh_from_db()

    assert tx.risk_score == 90
    assert customer.is_high_risk is True

    assert mock_alert.call_count == 2
    mock_audit.assert_called_once()
    mock_publish.assert_called_once_with(tx)
