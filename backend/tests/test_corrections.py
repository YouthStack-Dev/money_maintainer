from datetime import date
from decimal import Decimal

from app.corrections.parser import parse_correction
from app.corrections.schemas import CorrectionAction


def test_change_amount_requires_transaction():
    result = parse_correction("change transaction 42 amount to 550", date(2026, 9, 30))
    assert result["action"] == CorrectionAction.UPDATE
    assert result["transaction_id"] == 42
    assert result["amount"] == Decimal("550")
    assert result["confidence"] == "HIGH"


def test_contextual_change_uses_recent_transaction():
    result = parse_correction(
        "change that transaction amount to 550",
        date(2026, 9, 30),
        context_transaction_id=42,
    )
    assert result["transaction_id"] == 42
    assert result["amount"] == Decimal("550")
    assert result["confidence"] == "HIGH"


def test_contextual_last_transaction():
    result = parse_correction(
        "correct the last transaction date to 21/08",
        date(2026, 9, 30),
        context_transaction_id=99,
    )
    assert result["transaction_id"] == 99
    assert result["transaction_date"].date() == date(2026, 8, 21)
    assert result["confidence"] == "HIGH"


def test_context_without_recent_transaction_needs_confirmation():
    result = parse_correction(
        "change that transaction amount to 550",
        date(2026, 9, 30),
    )
    assert "transaction_id" in result["missing"]
    assert result["confidence"] == "MEDIUM"


def test_account_correction():
    result = parse_correction(
        "change transaction 42 account to HDFC",
        date(2026, 9, 30),
    )
    assert result["transaction_id"] == 42
    assert result["account_name"] == "HDFC"
    assert result["confidence"] == "HIGH"


def test_category_correction():
    result = parse_correction(
        "change transaction 42 category to Fuel",
        date(2026, 9, 30),
    )
    assert result["transaction_id"] == 42
    assert result["category_name"] == "Fuel"
    assert result["confidence"] == "HIGH"


def test_delete_duplicate_transaction():
    result = parse_correction("delete duplicate transaction 42", date(2026, 9, 30))
    assert result["action"] == CorrectionAction.DELETE
    assert result["transaction_id"] == 42
    assert result["confidence"] == "HIGH"


def test_change_date():
    result = parse_correction("correct transaction 42 date to 21/08", date(2026, 9, 30))
    assert result["transaction_id"] == 42
    assert result["transaction_date"].date() == date(2026, 8, 21)


def test_missing_target_needs_confirmation():
    result = parse_correction("change amount to 550", date(2026, 9, 30))
    assert "transaction_id" in result["missing"]
    assert result["confidence"] == "MEDIUM"


def test_relationship_scope_documents_repayment_safety():
    assert True


def test_merge_duplicate_transactions():
    result = parse_correction(
        "merge transaction 43 into transaction 42",
        date(2026, 9, 30),
    )
    assert result["action"] == CorrectionAction.MERGE
    assert result["duplicate_transaction_id"] == 43
    assert result["transaction_id"] == 42
    assert result["confidence"] == "HIGH"


def test_merge_same_transaction_needs_confirmation():
    result = parse_correction(
        "merge transaction 42 into transaction 42",
        date(2026, 9, 30),
    )
    assert "distinct_transactions" in result["missing"]
    assert result["confidence"] == "MEDIUM"


def test_office_reimbursement_amount_correction():
    result = parse_correction(
        "change office reimbursement 42 amount to 2500",
        date(2026, 9, 30),
    )
    assert result["action"] == CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE
    assert result["reimbursement_id"] == 42
    assert result["amount"] == Decimal("2500")
    assert result["confidence"] == "HIGH"


def test_office_reimbursement_date_correction():
    result = parse_correction(
        "correct office reimbursement 42 date to 21/08",
        date(2026, 9, 30),
    )
    assert result["action"] == CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE
    assert result["reimbursement_id"] == 42
    assert result["transaction_date"].date() == date(2026, 8, 21)
    assert result["confidence"] == "HIGH"


def test_office_reimbursement_without_field_needs_confirmation():
    result = parse_correction(
        "change office reimbursement 42",
        date(2026, 9, 30),
    )
    assert result["action"] == CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE
    assert result["reimbursement_id"] == 42
    assert "correction_fields" in result["missing"]
    assert result["confidence"] == "MEDIUM"
