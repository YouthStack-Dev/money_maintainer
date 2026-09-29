from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.budgets.models import Budget
from app.budgets.schemas import BudgetCreate, BudgetResponse, BudgetUpdate
from app.categories.models import Category, CategoryType
from app.core.database import get_db
from app.core.dependencies import current_user
from app.transactions.models import Transaction, TransactionType
from app.users.models import User

router = APIRouter()


def _get_budget(db, budget_id, user_id):
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id))
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


def _validate_category(db, user_id, category_id):
    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id,
            Category.is_active.is_(True),
            Category.category_type == CategoryType.EXPENSE,
        )
    )
    if not category:
        raise HTTPException(status_code=400, detail="Active expense category not found")


def _validate_period(start, end):
    if end < start:
        raise HTTPException(status_code=400, detail="period_end must be on or after period_start")


@router.get("", response_model=list[BudgetResponse])
def list_budgets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Budget).where(Budget.user_id == user.id).order_by(Budget.period_start.desc(), Budget.id.desc())
    ).all()


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _validate_category(db, user.id, payload.category_id)
    budget = Budget(user_id=user.id, **payload.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _get_budget(db, budget_id, user.id)


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, payload: BudgetUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    budget = _get_budget(db, budget_id, user.id)
    values = payload.model_dump(exclude_unset=True)
    category_id = values.get("category_id", budget.category_id)
    start = values.get("period_start", budget.period_start)
    end = values.get("period_end", budget.period_end)
    _validate_category(db, user.id, category_id)
    _validate_period(start, end)
    for field, value in values.items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    budget = _get_budget(db, budget_id, user.id)
    budget.is_active = False
    db.commit()
    return {"message": "Budget deactivated"}


@router.get("/{budget_id}/progress")
def budget_progress(budget_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    budget = _get_budget(db, budget_id, user.id)
    spent = db.scalar(
        select(__import__("sqlalchemy").func.coalesce(__import__("sqlalchemy").func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == user.id,
            Transaction.category_id == budget.category_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.is_active.is_(True),
            Transaction.transaction_date >= budget.period_start,
            Transaction.transaction_date <= budget.period_end,
        )
    ) or 0
    spent = float(spent)
    amount = float(budget.amount)
    return {
        "budget_id": budget.id,
        "budget_amount": amount,
        "spent": spent,
        "remaining": amount - spent,
        "percentage_used": (spent / amount * 100) if amount else 0,
        "over_budget": spent > amount,
    }
