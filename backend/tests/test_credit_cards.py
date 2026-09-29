from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.accounts.models import Account
from app.accounts.models import AccountType
from app.core.database import SessionLocal
from app.credit_cards.router import _next_due_date, _summary
from app.transactions.models import Transaction, TransactionType
from app.users.models import User


def test_next_due_date_moves_to_next_month_after_due_day():
    assert _next_due_date(date(2026, 9, 29), 15) == date(2026, 10, 15)


def test_next_due_date_handles_short_months():
    assert _next_due_date(date(2026, 2, 1), 31) == date(2026, 2, 28)


def test_credit_card_summary_uses_ledger_balance():
    db = SessionLocal()
    user = User(email=f"cc-{uuid4()}@x.test", full_name="Card", password_hash="x")
    db.add(user)
    db.flush()
    card = Account(
        user_id=user.id,
        name="SBI BPCL",
        account_type=AccountType.CREDIT_CARD,
        opening_balance=Decimal("0"),
        credit_limit=Decimal("50000"),
        statement_day=10,
        payment_due_day=25,
    )
    db.add(card)
    db.flush()
    db.add(
        Transaction(
            user_id=user.id,
            account_id=card.id,
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("12000"),
            transaction_date=date(2026, 9, 1),
            is_active=True,
        )
    )
    db.commit()

    summary = _summary(db, user.id, card)
    assert summary.outstanding_balance == Decimal("12000.00")
    assert summary.available_credit == Decimal("38000.00")
    assert summary.utilization_percent == Decimal("24.00")
    db.close()
