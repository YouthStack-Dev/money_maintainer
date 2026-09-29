from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.investments.models import InvestmentHolding
from app.investments.schemas import (
    InvestmentCreate,
    InvestmentResponse,
    InvestmentSummary,
    InvestmentUpdate,
)
from app.users.models import User

router = APIRouter()


def _get_holding(db: Session, user_id: int, holding_id: int) -> InvestmentHolding:
    holding = db.scalar(
        select(InvestmentHolding).where(
            InvestmentHolding.id == holding_id,
            InvestmentHolding.user_id == user_id,
        )
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Investment holding not found")
    return holding


def _response(holding: InvestmentHolding) -> InvestmentResponse:
    invested = holding.invested_value
    market = holding.market_value
    gain = market - invested
    return InvestmentResponse(
        id=holding.id,
        investment_type=holding.investment_type,
        symbol=holding.symbol,
        name=holding.name,
        quantity=holding.quantity,
        average_cost=holding.average_cost,
        current_price=holding.current_price,
        currency=holding.currency,
        notes=holding.notes,
        is_active=holding.is_active,
        invested_value=invested,
        market_value=market,
        unrealized_gain_loss=gain,
        unrealized_return_percent=(
            (gain / invested * Decimal("100")).quantize(Decimal("0.01"))
            if invested else Decimal("0")
        ),
        created_at=holding.created_at,
        updated_at=holding.updated_at,
    )


@router.get("", response_model=list[InvestmentResponse])
def list_investments(
    user: User = Depends(current_user), db: Session = Depends(get_db)
):
    holdings = db.scalars(
        select(InvestmentHolding)
        .where(
            InvestmentHolding.user_id == user.id,
            InvestmentHolding.is_active.is_(True),
        )
        .order_by(InvestmentHolding.name.asc(), InvestmentHolding.id.asc())
    ).all()
    return [_response(holding) for holding in holdings]


@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def create_investment(
    payload: InvestmentCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    holding = InvestmentHolding(user_id=user.id, **payload.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return _response(holding)


@router.get("/summary", response_model=InvestmentSummary)
def investment_summary(
    user: User = Depends(current_user), db: Session = Depends(get_db)
):
    holdings = db.scalars(
        select(InvestmentHolding).where(
            InvestmentHolding.user_id == user.id,
            InvestmentHolding.is_active.is_(True),
        )
    ).all()
    invested = sum((h.invested_value for h in holdings), Decimal("0"))
    market = sum((h.market_value for h in holdings), Decimal("0"))
    gain = market - invested
    return InvestmentSummary(
        holding_count=len(holdings),
        invested_value=invested,
        market_value=market,
        unrealized_gain_loss=gain,
        unrealized_return_percent=(
            (gain / invested * Decimal("100")).quantize(Decimal("0.01"))
            if invested else Decimal("0")
        ),
    )


@router.get("/{holding_id}", response_model=InvestmentResponse)
def get_investment(
    holding_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _response(_get_holding(db, user.id, holding_id))


@router.patch("/{holding_id}", response_model=InvestmentResponse)
def update_investment(
    holding_id: int,
    payload: InvestmentUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    holding = _get_holding(db, user.id, holding_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(holding, field, value)
    db.commit()
    db.refresh(holding)
    return _response(holding)


@router.delete("/{holding_id}")
def delete_investment(
    holding_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    holding = _get_holding(db, user.id, holding_id)
    holding.is_active = False
    db.commit()
    return {"message": "Investment holding deactivated"}
