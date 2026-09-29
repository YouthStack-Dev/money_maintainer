from calendar import monthrange
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.core.database import get_db
from app.core.dependencies import current_user
from app.transactions.models import Transaction, TransactionType
from app.credit_cards.schemas import CreditCardSettingsUpdate, CreditCardSummary
from app.users.models import User

router = APIRouter()


def _get_card(db: Session, user_id: int, account_id: int) -> Account:
    card = db.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == user_id,
            Account.account_type == AccountType.CREDIT_CARD,
        )
    )
    if not card:
        raise HTTPException(404, "Credit card account not found")
    return card


def _next_due_date(today: date, due_day: int) -> date:
    if today.day <= min(due_day, monthrange(today.year, today.month)[1]):
        return date(today.year, today.month, min(due_day, monthrange(today.year, today.month)[1]))
    year, month = today.year, today.month + 1
    if month == 13:
        year, month = year + 1, 1
    return date(year, month, min(due_day, monthrange(year, month)[1]))


def _current_balance(db: Session, user_id: int, card: Account) -> Decimal:
    balance = Decimal(card.opening_balance)
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
            (Transaction.account_id == card.id) | (Transaction.transfer_account_id == card.id),
        )
    ).all()
    for tx in transactions:
        amount = Decimal(tx.amount)
        if tx.transaction_type in (TransactionType.INCOME, TransactionType.REFUND):
            if tx.account_id == card.id:
                balance += amount
            elif tx.transfer_account_id == card.id:
                balance += amount
        elif tx.transaction_type == TransactionType.EXPENSE:
            if tx.account_id == card.id:
                balance -= amount
        elif tx.transaction_type == TransactionType.TRANSFER:
            if tx.account_id == card.id:
                balance -= amount
            elif tx.transfer_account_id == card.id:
                balance += amount
    return balance


def _summary(db: Session, user_id: int, card: Account) -> CreditCardSummary:
    if card.credit_limit is None or card.statement_day is None or card.payment_due_day is None:
        raise HTTPException(409, "Credit card settings are not configured")

    balance = _current_balance(db, user_id, card)
    outstanding = max(-balance, Decimal("0"))
    available = max(card.credit_limit - outstanding, Decimal("0"))
    utilization = (outstanding / card.credit_limit * Decimal("100")).quantize(Decimal("0.01"))

    return CreditCardSummary(
        account_id=card.id,
        name=card.name,
        institution_name=card.institution_name,
        credit_limit=card.credit_limit,
        current_balance=balance,
        outstanding_balance=outstanding,
        available_credit=available,
        utilization_percent=utilization,
        statement_day=card.statement_day,
        payment_due_day=card.payment_due_day,
        next_payment_due_date=_next_due_date(date.today(), card.payment_due_day),
        is_active=card.is_active,
    )


@router.get("", response_model=list[CreditCardSummary])
def list_credit_cards(user: User = Depends(current_user), db: Session = Depends(get_db)):
    cards = db.scalars(
        select(Account)
        .where(Account.user_id == user.id, Account.account_type == AccountType.CREDIT_CARD)
        .order_by(Account.id)
    ).all()
    return [_summary(db, user.id, card) for card in cards if card.credit_limit is not None]


@router.get("/{account_id}", response_model=CreditCardSummary)
def get_credit_card(account_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _summary(db, user.id, _get_card(db, user.id, account_id))


@router.put("/{account_id}", response_model=CreditCardSummary)
def configure_credit_card(
    account_id: int,
    payload: CreditCardSettingsUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    card = _get_card(db, user.id, account_id)
    card.credit_limit = payload.credit_limit
    card.statement_day = payload.statement_day
    card.payment_due_day = payload.payment_due_day
    db.commit()
    db.refresh(card)
    return _summary(db, user.id, card)
