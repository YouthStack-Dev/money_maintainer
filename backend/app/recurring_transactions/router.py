from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.recurring_transactions.models import RecurringTransaction
from app.recurring_transactions.schemas import (
    RecurringTransactionCreate, RecurringTransactionGenerationResponse,
    RecurringTransactionResponse, RecurringTransactionUpdate,
)
from app.recurring_transactions.service import create_template, generate_next, validate_dependencies
from app.transactions.models import TransactionType
from app.users.models import User

router = APIRouter()


def _get(db: Session, recurring_id: int, user_id: int) -> RecurringTransaction:
    item = db.scalar(select(RecurringTransaction).where(RecurringTransaction.id == recurring_id, RecurringTransaction.user_id == user_id))
    if not item:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    return item


@router.get("", response_model=list[RecurringTransactionResponse])
def list_recurring_transactions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(RecurringTransaction).where(RecurringTransaction.user_id == user.id).order_by(RecurringTransaction.id)).all()


@router.post("", response_model=RecurringTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_recurring_transaction(payload: RecurringTransactionCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        return create_template(db, user.id, payload.model_dump())
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{recurring_id}", response_model=RecurringTransactionResponse)
def get_recurring_transaction(recurring_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _get(db, recurring_id, user.id)


@router.patch("/{recurring_id}", response_model=RecurringTransactionResponse)
def update_recurring_transaction(recurring_id: int, payload: RecurringTransactionUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = _get(db, recurring_id, user.id)
    values = payload.model_dump(exclude_unset=True)
    effective = {
        "account_id": values.get("account_id", item.account_id),
        "category_id": values.get("category_id", item.category_id),
        "transaction_type": values.get("transaction_type", TransactionType(item.transaction_type)),
    }
    if effective["transaction_type"] == TransactionType.TRANSFER:
        raise HTTPException(status_code=400, detail="Recurring transfers are not supported")
    start = values.get("start_date", item.start_date)
    end = values.get("end_date", item.end_date)
    if end is not None and end < start:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")
    try:
        validate_dependencies(db, user.id, **effective)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    for field, value in values.items():
        setattr(item, field, value)
    if "start_date" in values:
        item.next_run_at = __import__("datetime").datetime.combine(values["start_date"], __import__("datetime").datetime.min.time(), tzinfo=__import__("datetime").timezone.utc)
        item.last_run_at = None
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{recurring_id}")
def delete_recurring_transaction(recurring_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = _get(db, recurring_id, user.id)
    item.is_active = False
    db.commit()
    return {"message": "Recurring transaction deactivated"}


@router.post("/{recurring_id}/generate", response_model=RecurringTransactionGenerationResponse)
def generate_recurring_transaction(recurring_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        item, transaction, scheduled = generate_next(db, user.id, recurring_id)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RecurringTransactionGenerationResponse(
        recurring_transaction_id=item.id,
        transaction_id=transaction.id,
        scheduled_run_at=scheduled,
        next_run_at=item.next_run_at,
        is_active=item.is_active,
    )
