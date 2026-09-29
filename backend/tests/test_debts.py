from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.accounts.models import Account
from app.core.database import SessionLocal
from app.debts.models import DebtDirection, DebtStatus
from app.debts.service import create_debt, repay_debt
from app.transactions.models import Transaction, TransactionType
from app.users.models import User


@pytest.fixture
def data():
    db = SessionLocal()
    user = User(email=f"d-{uuid4()}@x.test", full_name="Debt", password_hash="x")
    db.add(user)
    db.flush()
    account = Account(user_id=user.id, name="Bank", account_type="BANK_ACCOUNT")
    db.add(account)
    db.commit()
    db.refresh(account)
    yield db, user, account
    db.close()


@pytest.mark.parametrize(
    "direction,opening_type,repayment_type",
    [
        (DebtDirection.BORROWED, TransactionType.INCOME, TransactionType.EXPENSE),
        (DebtDirection.LENT, TransactionType.EXPENSE, TransactionType.INCOME),
    ],
)
def test_debt_lifecycle_and_ledger(data, direction, opening_type, repayment_type):
    db, user, account = data
    debt = create_debt(
        db,
        user.id,
        {
            "direction": direction,
            "account_id": account.id,
            "person_name": "Alex",
            "description": None,
            "original_amount": Decimal("1000"),
            "due_date": None,
        },
    )

    opening = db.query(Transaction).filter(Transaction.user_id == user.id).one()
    assert opening.transaction_type == opening_type
    assert opening.amount == Decimal("1000.00")

    debt, repayment, transaction = repay_debt(
        db,
        user.id,
        debt.id,
        {
            "account_id": account.id,
            "amount": Decimal("400"),
            "repayment_date": date(2026, 9, 29),
            "note": "partial",
        },
    )
    assert debt.outstanding_amount == Decimal("600.00")
    assert debt.status == DebtStatus.PARTIALLY_PAID
    assert transaction.transaction_type == repayment_type
    assert db.query(Transaction).filter(Transaction.user_id == user.id).count() == 2

    debt, _, _ = repay_debt(
        db,
        user.id,
        debt.id,
        {
            "account_id": account.id,
            "amount": Decimal("600"),
            "repayment_date": date(2026, 10, 1),
            "note": "final",
        },
    )
    assert debt.outstanding_amount == Decimal("0.00")
    assert debt.status == DebtStatus.SETTLED


def test_repayment_cannot_exceed_balance(data):
    db, user, account = data
    debt = create_debt(
        db,
        user.id,
        {
            "direction": DebtDirection.BORROWED,
            "account_id": account.id,
            "person_name": "Alex",
            "description": None,
            "original_amount": Decimal("100"),
            "due_date": None,
        },
    )
    with pytest.raises(ValueError):
        repay_debt(
            db,
            user.id,
            debt.id,
            {
                "account_id": account.id,
                "amount": Decimal("101"),
                "repayment_date": date(2026, 9, 29),
                "note": None,
            },
        )


def test_create_requires_active_owned_account(data):
    db, user, _ = data
    with pytest.raises(ValueError):
        create_debt(
            db,
            user.id,
            {
                "direction": DebtDirection.LENT,
                "account_id": 999999,
                "person_name": "Alex",
                "description": None,
                "original_amount": Decimal("100"),
                "due_date": None,
            },
        )
