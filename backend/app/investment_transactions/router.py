from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.investments.models import InvestmentHolding
from app.investment_transactions.models import InvestmentTransaction, InvestmentTransactionType
from app.investment_transactions.schemas import InvestmentTransactionCreate, InvestmentTransactionResponse
from app.users.models import User

router = APIRouter()


def _realized_gain(tx: InvestmentTransaction, holding: InvestmentHolding) -> Decimal | None:
    if tx.transaction_type != InvestmentTransactionType.SELL:
        return None
    return (tx.quantity * (tx.price - holding.average_cost)) - tx.fees


def _response(tx: InvestmentTransaction, holding: InvestmentHolding) -> InvestmentTransactionResponse:
    return InvestmentTransactionResponse(
        id=tx.id,
        holding_id=tx.holding_id,
        transaction_type=tx.transaction_type,
        quantity=tx.quantity,
        price=tx.price,
        fees=tx.fees,
        transaction_date=tx.transaction_date,
        notes=tx.notes,
        gross_value=tx.gross_value,
        cash_value=tx.cash_value,
        realized_gain_loss=_realized_gain(tx, holding),
        created_at=tx.created_at,
    )


def _holding(db: Session, user_id: int, holding_id: int) -> InvestmentHolding:
    holding = db.scalar(
        select(InvestmentHolding)
        .where(
            InvestmentHolding.id == holding_id,
            InvestmentHolding.user_id == user_id,
            InvestmentHolding.is_active.is_(True),
        )
        .with_for_update()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Investment holding not found")
    return holding


@router.get("", response_model=list[InvestmentTransactionResponse])
def list_transactions(
    holding_id: int | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    stmt = select(InvestmentTransaction).where(InvestmentTransaction.user_id == user.id)
    if holding_id is not None:
        stmt = stmt.where(InvestmentTransaction.holding_id == holding_id)
    transactions = db.scalars(
        stmt.order_by(InvestmentTransaction.transaction_date.desc(), InvestmentTransaction.id.desc())
    ).all()
    holdings = {
        h.id: h for h in db.scalars(
            select(InvestmentHolding).where(InvestmentHolding.user_id == user.id)
        ).all()
    }
    return [_response(tx, holdings[tx.holding_id]) for tx in transactions]


@router.post("", response_model=InvestmentTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: InvestmentTransactionCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    holding = _holding(db, user.id, payload.holding_id)
    quantity = payload.quantity
    fees = payload.fees

    if payload.transaction_type == InvestmentTransactionType.SELL:
        if quantity > holding.quantity:
            raise HTTPException(status_code=400, detail="Sell quantity exceeds holding quantity")
        realized = (quantity * (payload.price - holding.average_cost)) - fees
        holding.quantity -= quantity
        if holding.quantity == 0:
            holding.average_cost = Decimal("0")
        else:
            holding.average_cost = holding.average_cost
    else:
        old_cost = holding.quantity * holding.average_cost
        new_cost = quantity * payload.price + fees
        new_quantity = holding.quantity + quantity
        holding.average_cost = (old_cost + new_cost) / new_quantity
        holding.quantity = new_quantity

    tx = InvestmentTransaction(user_id=user.id, **payload.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return _response(tx, holding)


@router.get("/summary", response_model=dict)
def transaction_summary(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    transactions = db.scalars(
        select(InvestmentTransaction).where(InvestmentTransaction.user_id == user.id)
    ).all()
    realized = Decimal("0")
    invested = Decimal("0")
    proceeds = Decimal("0")
    for tx in transactions:
        if tx.transaction_type == InvestmentTransactionType.BUY:
            invested += tx.cash_value
        else:
            proceeds += tx.cash_value
            holding = db.get(InvestmentHolding, tx.holding_id)
            realized += _realized_gain(tx, holding) if holding else Decimal("0")
    return {
        "transaction_count": len(transactions),
        "buy_value": invested,
        "sell_proceeds": proceeds,
        "realized_gain_loss": realized,
    }
