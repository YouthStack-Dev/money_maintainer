from datetime import datetime, time, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.cash_flow.models import CashFlowItem, CashFlowPlan, CashFlowType
from app.cash_flow.schemas import (
    CashFlowForecast, CashFlowItemCreate, CashFlowItemResponse, CashFlowItemUpdate,
    CashFlowPlanCreate, CashFlowPlanResponse, CashFlowPlanUpdate,
)
from app.categories.models import Category, CategoryType
from app.core.database import get_db
from app.core.dependencies import current_user
from app.transactions.models import Transaction, TransactionType
from app.users.models import User

router = APIRouter()


def _plan(db: Session, plan_id: int, user_id: int) -> CashFlowPlan:
    plan = db.scalar(select(CashFlowPlan).where(CashFlowPlan.id == plan_id, CashFlowPlan.user_id == user_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Cash-flow plan not found")
    return plan


def _validate_refs(db, user_id, flow_type, category_id, account_id):
    if account_id is not None and not db.scalar(select(Account.id).where(Account.id == account_id, Account.user_id == user_id, Account.is_active.is_(True))):
        raise HTTPException(status_code=400, detail="Active account not found")
    if category_id is not None:
        expected = CategoryType.INCOME if flow_type == CashFlowType.INCOME else CategoryType.EXPENSE
        if not db.scalar(select(Category.id).where(Category.id == category_id, Category.user_id == user_id, Category.is_active.is_(True), Category.category_type == expected)):
            raise HTTPException(status_code=400, detail="Active category with matching type not found")


@router.get("", response_model=list[CashFlowPlanResponse])
def list_plans(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(CashFlowPlan).where(CashFlowPlan.user_id == user.id).order_by(CashFlowPlan.start_date.desc(), CashFlowPlan.id.desc())).all()


@router.post("", response_model=CashFlowPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(payload: CashFlowPlanCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = CashFlowPlan(user_id=user.id, **payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/{plan_id}", response_model=CashFlowPlanResponse)
def get_plan(plan_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _plan(db, plan_id, user.id)


@router.patch("/{plan_id}", response_model=CashFlowPlanResponse)
def update_plan(plan_id: int, payload: CashFlowPlanUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = _plan(db, plan_id, user.id)
    values = payload.model_dump(exclude_unset=True)
    start, end = values.get("start_date", plan.start_date), values.get("end_date", plan.end_date)
    if end < start:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")
    for field, value in values.items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = _plan(db, plan_id, user.id)
    plan.is_active = False
    db.commit()
    return {"message": "Cash-flow plan deactivated"}


@router.get("/{plan_id}/items", response_model=list[CashFlowItemResponse])
def list_items(plan_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = _plan(db, plan_id, user.id)
    return db.scalars(select(CashFlowItem).where(CashFlowItem.plan_id == plan.id).order_by(CashFlowItem.planned_date, CashFlowItem.id)).all()


@router.post("/{plan_id}/items", response_model=CashFlowItemResponse, status_code=status.HTTP_201_CREATED)
def add_item(plan_id: int, payload: CashFlowItemCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = _plan(db, plan_id, user.id)
    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Inactive plan cannot receive items")
    if payload.planned_date < plan.start_date or payload.planned_date > plan.end_date:
        raise HTTPException(status_code=400, detail="planned_date must be within the plan period")
    _validate_refs(db, user.id, payload.flow_type, payload.category_id, payload.account_id)
    item = CashFlowItem(plan_id=plan.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{plan_id}/items/{item_id}", response_model=CashFlowItemResponse)
def update_item(plan_id: int, item_id: int, payload: CashFlowItemUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = _plan(db, plan_id, user.id)
    item = db.scalar(select(CashFlowItem).where(CashFlowItem.id == item_id, CashFlowItem.plan_id == plan.id))
    if not item:
        raise HTTPException(status_code=404, detail="Cash-flow item not found")
    values = payload.model_dump(exclude_unset=True)
    flow_type = values.get("flow_type", item.flow_type)
    planned_date = values.get("planned_date", item.planned_date)
    if planned_date < plan.start_date or planned_date > plan.end_date:
        raise HTTPException(status_code=400, detail="planned_date must be within the plan period")
    _validate_refs(db, user.id, flow_type, values.get("category_id", item.category_id), values.get("account_id", item.account_id))
    for field, value in values.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{plan_id}/items/{item_id}")
def delete_item(plan_id: int, item_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _plan(db, plan_id, user.id)
    item = db.scalar(select(CashFlowItem).where(CashFlowItem.id == item_id, CashFlowItem.plan_id == plan_id))
    if not item:
        raise HTTPException(status_code=404, detail="Cash-flow item not found")
    item.is_active = False
    db.commit()
    return {"message": "Cash-flow item deactivated"}


@router.get("/{plan_id}/forecast", response_model=CashFlowForecast)
def forecast(plan_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    plan = _plan(db, plan_id, user.id)
    planned_income = db.scalar(select(func.coalesce(func.sum(CashFlowItem.amount), 0)).where(CashFlowItem.plan_id == plan.id, CashFlowItem.is_active.is_(True), CashFlowItem.flow_type == CashFlowType.INCOME)) or 0
    planned_expenses = db.scalar(select(func.coalesce(func.sum(CashFlowItem.amount), 0)).where(CashFlowItem.plan_id == plan.id, CashFlowItem.is_active.is_(True), CashFlowItem.flow_type == CashFlowType.EXPENSE)) or 0
    start_dt = datetime.combine(plan.start_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(plan.end_date, time.max, tzinfo=timezone.utc)
    actual_income = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user.id, Transaction.transaction_type == TransactionType.INCOME, Transaction.is_active.is_(True), Transaction.transaction_date.between(start_dt, end_dt))) or 0
    actual_expenses = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user.id, Transaction.transaction_type == TransactionType.EXPENSE, Transaction.is_active.is_(True), Transaction.transaction_date.between(start_dt, end_dt))) or 0
    planned_net = Decimal(planned_income) - Decimal(planned_expenses)
    actual_net = Decimal(actual_income) - Decimal(actual_expenses)
    return CashFlowForecast(
        plan_id=plan.id,
        planned_income=Decimal(planned_income),
        planned_expenses=Decimal(planned_expenses),
        planned_net_cash_flow=planned_net,
        projected_ending_balance=plan.starting_balance + planned_net,
        actual_income=Decimal(actual_income),
        actual_expenses=Decimal(actual_expenses),
        actual_net_cash_flow=actual_net,
        variance=actual_net - planned_net,
    )
