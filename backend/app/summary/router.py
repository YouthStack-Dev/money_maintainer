from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.core.database import get_db
from app.core.dependencies import current_user
from app.transactions.models import Transaction, TransactionType
from app.users.models import User

router = APIRouter()


def _sum_transactions(db: Session, user_id: int, account_id: int | None = None):
    q = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.is_active.is_(True),
    )
    if account_id is not None:
        q = q.where(
            (Transaction.account_id == account_id)
            | (Transaction.transfer_account_id == account_id)
        )
    return db.scalars(q).all()


@router.get("")
def financial_summary(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    accounts = db.scalars(
        select(Account).where(Account.user_id == user.id, Account.is_active.is_(True))
    ).all()
    transactions = _sum_transactions(db, user.id)

    balances = {account.id: Decimal(account.opening_balance) for account in accounts}
    income = Decimal("0")
    expense = Decimal("0")
    refunds = Decimal("0")

    for tx in transactions:
        amount = Decimal(tx.amount)
        if tx.transaction_type == TransactionType.INCOME:
            balances[tx.account_id] += amount
            income += amount
        elif tx.transaction_type == TransactionType.EXPENSE:
            balances[tx.account_id] -= amount
            expense += amount
        elif tx.transaction_type == TransactionType.REFUND:
            balances[tx.account_id] += amount
            refunds += amount
        elif tx.transaction_type == TransactionType.TRANSFER:
            balances[tx.account_id] -= amount
            if tx.transfer_account_id in balances:
                balances[tx.transfer_account_id] += amount

    total_assets = sum(
        (balances[a.id] for a in accounts if a.account_type != AccountType.CREDIT_CARD),
        Decimal("0"),
    )
    credit_card_debt = sum(
        (max(-balances[a.id], Decimal("0")) for a in accounts if a.account_type == AccountType.CREDIT_CARD),
        Decimal("0"),
    )

    return {
        "income": income,
        "expenses": expense,
        "refunds": refunds,
        "net_cash_flow": income + refunds - expense,
        "total_assets": total_assets,
        "credit_card_debt": credit_card_debt,
        "net_worth": total_assets - credit_card_debt,
        "accounts": [
            {
                "id": a.id,
                "name": a.name,
                "account_type": a.account_type,
                "opening_balance": a.opening_balance,
                "current_balance": balances[a.id],
            }
            for a in accounts
        ],
    }
