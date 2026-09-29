from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.transactions.models import TransactionType
from app.transactions.schemas import TransactionCreate, TransactionUpdate


def test_expense_transaction():
    tx = TransactionCreate(
        account_id=1,
        category_id=2,
        transaction_type=TransactionType.EXPENSE,
        amount=Decimal("500.00"),
        transaction_date=datetime.now(timezone.utc),
    )
    assert tx.amount == Decimal("500.00")
    assert tx.transfer_account_id is None


def test_transfer_requires_destination():
    with pytest.raises(ValidationError):
        TransactionCreate(
            account_id=1,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("1000.00"),
            transaction_date=datetime.now(timezone.utc),
        )


def test_transfer_cannot_have_category():
    with pytest.raises(ValidationError):
        TransactionCreate(
            account_id=1,
            category_id=2,
            transfer_account_id=3,
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("1000.00"),
            transaction_date=datetime.now(timezone.utc),
        )


def test_transfer_accounts_must_be_distinct():
    update = TransactionUpdate(
        account_id=1,
        transfer_account_id=1,
        transaction_type=TransactionType.TRANSFER,
    )
    assert update.transfer_account_id == 1
