from datetime import date
from decimal import Decimal

from app.quick_entry.parser import extract_amount, extract_date, infer_type, parse_entry, split_entries
from app.transactions.models import TransactionType


def test_split_entries_supports_semicolon_and_newline():
    assert split_entries("110 petrol; 100 snacks\n200 bike wash") == [
        "110 petrol",
        "100 snacks",
        "200 bike wash",
    ]


def test_extract_amount_supports_rupees_and_commas():
    amount, remainder = extract_amount("₹1,250 petrol")
    assert amount == Decimal("1250")
    assert remainder == "petrol"


def test_extract_date_supports_numeric_date():
    parsed, remainder, explicit = extract_date("21/08 250 tiffin", date(2026, 9, 30))
    assert parsed == date(2026, 8, 21)
    assert remainder == "250 tiffin"
    assert explicit is True


def test_extract_date_supports_named_month():
    parsed, remainder, explicit = extract_date("Sep 1, 110 petrol", date(2026, 9, 30))
    assert parsed == date(2026, 9, 1)
    assert remainder == "110 petrol"
    assert explicit is True


def test_infer_type_defaults_to_expense():
    assert infer_type("110 petrol") == TransactionType.EXPENSE


def test_infer_type_recognizes_income_refund_and_transfer():
    assert infer_type("salary 29800") == TransactionType.INCOME
    assert infer_type("refund 2000") == TransactionType.REFUND
    assert infer_type("transfer 5000") == TransactionType.TRANSFER


def test_parse_entry_inherits_previous_batch_date():
    parsed = parse_entry("200 bike wash", date(2026, 9, 30), date(2026, 8, 22))
    assert parsed["transaction_date"].date() == date(2026, 8, 22)
    assert parsed["explicit_date"] is False
