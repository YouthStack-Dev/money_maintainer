from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.core.database import get_db
from app.core.dependencies import current_user
from app.debts.models import Debt, DebtDirection, DebtStatus
from app.investments.models import InvestmentHolding
from app.assets.models import Asset
from app.transactions.models import Transaction, TransactionType
from app.net_worth.models import NetWorthSnapshot
from app.net_worth.schemas import (
    NetWorthCurrentResponse,
    NetWorthSnapshotGenerate,
    NetWorthSnapshotResponse,
)
from app.users.models import User

router = APIRouter()


def _calculate_values(
    accounts: list[Account],
    transactions: list[Transaction],
    investments: list[InvestmentHolding],
    assets: list[Asset],
    debts: list[Debt],
) -> dict[str, Decimal]:
    balances = {account.id: Decimal(account.opening_balance) for account in accounts}

    for tx in transactions:
        amount = Decimal(tx.amount)
        if tx.transaction_type in {TransactionType.INCOME, TransactionType.REFUND}:
            balances[tx.account_id] += amount
        elif tx.transaction_type == TransactionType.EXPENSE:
            balances[tx.account_id] -= amount
        elif tx.transaction_type == TransactionType.TRANSFER:
            balances[tx.account_id] -= amount
            if tx.transfer_account_id in balances:
                balances[tx.transfer_account_id] += amount

    liquid_assets = sum(
        (
            balances[account.id]
            for account in accounts
            if account.account_type != AccountType.CREDIT_CARD
        ),
        Decimal("0"),
    )
    credit_card_debt = sum(
        (
            max(-balances[account.id], Decimal("0"))
            for account in accounts
            if account.account_type == AccountType.CREDIT_CARD
        ),
        Decimal("0"),
    )
    investment_value = sum(
        (holding.market_value for holding in investments),
        Decimal("0"),
    )
    other_assets = sum(
        (Decimal(asset.current_value) for asset in assets),
        Decimal("0"),
    )
    lent_receivables = sum(
        (
            Decimal(debt.outstanding_amount)
            for debt in debts
            if debt.direction == DebtDirection.LENT
            and debt.status != DebtStatus.CANCELLED
        ),
        Decimal("0"),
    )
    borrowed_debt = sum(
        (
            Decimal(debt.outstanding_amount)
            for debt in debts
            if debt.direction == DebtDirection.BORROWED
            and debt.status != DebtStatus.CANCELLED
        ),
        Decimal("0"),
    )

    total_assets = liquid_assets + investment_value + other_assets + lent_receivables
    total_liabilities = credit_card_debt + borrowed_debt

    return {
        "liquid_assets": liquid_assets,
        "investment_value": investment_value,
        "other_assets": other_assets,
        "lent_receivables": lent_receivables,
        "credit_card_debt": credit_card_debt,
        "borrowed_debt": borrowed_debt,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets - total_liabilities,
    }


def _load_values(db: Session, user_id: int) -> dict[str, Decimal]:
    accounts = db.scalars(
        select(Account).where(Account.user_id == user_id)
    ).all()
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
        )
    ).all()
    investments = db.scalars(
        select(InvestmentHolding).where(
            InvestmentHolding.user_id == user_id,
            InvestmentHolding.is_active.is_(True),
        )
    ).all()
    assets = db.scalars(
        select(Asset).where(
            Asset.user_id == user_id,
            Asset.is_active.is_(True),
        )
    ).all()
    debts = db.scalars(
        select(Debt).where(Debt.user_id == user_id)
    ).all()

    return _calculate_values(accounts, transactions, investments, assets, debts)


@router.get("", response_model=list[NetWorthSnapshotResponse])
def list_snapshots(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(NetWorthSnapshot)
        .where(NetWorthSnapshot.user_id == user.id)
        .order_by(NetWorthSnapshot.snapshot_date.desc(), NetWorthSnapshot.id.desc())
    ).all()


@router.get("/current", response_model=NetWorthCurrentResponse)
def current_net_worth(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    values = _load_values(db, user.id)
    return NetWorthCurrentResponse(snapshot_date=date.today(), **values)


@router.post(
    "/snapshots/generate",
    response_model=NetWorthSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_snapshot(
    payload: NetWorthSnapshotGenerate | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    snapshot_date = (payload.snapshot_date if payload else None) or date.today()
    values = _load_values(db, user.id)

    snapshot = db.scalar(
        select(NetWorthSnapshot).where(
            NetWorthSnapshot.user_id == user.id,
            NetWorthSnapshot.snapshot_date == snapshot_date,
        )
    )
    if snapshot:
        for field, value in values.items():
            setattr(snapshot, field, value)
    else:
        snapshot = NetWorthSnapshot(
            user_id=user.id,
            snapshot_date=snapshot_date,
            **values,
        )
        db.add(snapshot)

    db.commit()
    db.refresh(snapshot)
    return snapshot


@router.get("/snapshots/{snapshot_id}", response_model=NetWorthSnapshotResponse)
def get_snapshot(
    snapshot_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    snapshot = db.scalar(
        select(NetWorthSnapshot).where(
            NetWorthSnapshot.id == snapshot_id,
            NetWorthSnapshot.user_id == user.id,
        )
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Net-worth snapshot not found")
    return snapshot
