from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.budgets.schemas import BudgetCreate
from app.transactions.models import TransactionType


def test_budget_period():
    b = BudgetCreate(
        category_id=1,
        name="September Food",
        amount=Decimal("5000.00"),
        period_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        period_end=datetime(2026, 9, 30, tzinfo=timezone.utc),
    )
    assert b.amount == Decimal("5000.00")


def test_budget_rejects_reverse_period():
    with pytest.raises(ValidationError):
        BudgetCreate(
            category_id=1,
            name="Invalid",
            amount=Decimal("5000"),
            period_start=datetime(2026, 9, 30, tzinfo=timezone.utc),
            period_end=datetime(2026, 9, 1, tzinfo=timezone.utc),
        )


def test_budget_amount_positive():
    with pytest.raises(ValidationError):
        BudgetCreate(
            category_id=1,
            name="Invalid",
            amount=Decimal("0"),
            period_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
            period_end=datetime(2026, 9, 30, tzinfo=timezone.utc),
        )
