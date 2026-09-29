from datetime import date
from decimal import Decimal

from app.quick_entry.parser import extract_amount, extract_date, infer_type, split_entries


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
    parsed, remainder = extract_date("21/08 250 tiffin", date(2026, 9, 30))
    assert parsed == date(2026, 8, 21)
    assert remainder == "250 tiffin"


def test_extract_date_supports_named_month():
    parsed, remainder = extract_date("Sep 1, 110 petrol", date(2026, 9, 30))
    assert parsed == date(2026, 9, 1)
    assert remainder == ", 110 petrol"


def test_infer_type_defaults_to_expense():
    from app.transactions.models import TransactionType

    assert infer_type("110 petrol") == TransactionType.EXPENSE
