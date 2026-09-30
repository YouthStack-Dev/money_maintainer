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
