from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.alerts.models import AlertSeverity, AlertType, FinancialAlert
from app.alerts.schemas import AlertResponse, AlertSummary
from app.core.database import get_db
from app.core.dependencies import current_user
from app.accounts.models import Account, AccountType
from app.credit_cards.router import _current_balance
from app.debts.models import Debt, DebtStatus
from app.goals.models import FinancialGoal, GoalStatus
from app.users.models import User

router = APIRouter()

def _alerts(db: Session, user_id: int):
    today = date.today()
    cards = db.scalars(select(Account).where(Account.user_id == user_id, Account.account_type == AccountType.CREDIT_CARD, Account.is_active.is_(True), Account.credit_limit.is_not(None), Account.payment_due_day.is_not(None))).all()
    for card in cards:
        balance = _current_balance(db, user_id, card)
        outstanding = max(-balance, Decimal("0"))
        if outstanding > card.credit_limit:
            yield (AlertType.CREDIT_CARD_OVER_LIMIT, AlertSeverity.CRITICAL, f"{card.name} is over limit", f"Outstanding ₹{outstanding:.2f} exceeds limit ₹{card.credit_limit:.2f} by ₹{outstanding-card.credit_limit:.2f}.", card.id)
        due_day = min(card.payment_due_day, 31)
        due = date(today.year, today.month, min(due_day, __import__('calendar').monthrange(today.year, today.month)[1]))
        if due < today:
            if today.month == 12: due = date(today.year+1,1,min(due_day,31))
            else: due = date(today.year,today.month+1,min(due_day,__import__('calendar').monthrange(today.year,today.month+1)[1]))
        days = (due-today).days
        if outstanding > 0 and days <= 3:
            yield (AlertType.CREDIT_CARD_DUE, AlertSeverity.WARNING, f"{card.name} payment due soon", f"₹{outstanding:.2f} outstanding; payment due in {days} day(s).", card.id)

    debts = db.scalars(select(Debt).where(Debt.user_id == user_id, Debt.status.in_([DebtStatus.ACTIVE, DebtStatus.PARTIALLY_PAID]), Debt.due_date.is_not(None))).all()
    for debt in debts:
        days = (debt.due_date - today).days
        if days < 0:
            yield (AlertType.DEBT_OVERDUE, AlertSeverity.CRITICAL, f"{debt.person_name} debt is overdue", f"₹{debt.outstanding_amount:.2f} remains outstanding; due date was {debt.due_date}.", debt.id)
        elif days <= 3:
            yield (AlertType.DEBT_DUE, AlertSeverity.WARNING, f"{debt.person_name} debt is due soon", f"₹{debt.outstanding_amount:.2f} remains outstanding; due in {days} day(s).", debt.id)

    goals = db.scalars(select(FinancialGoal).where(FinancialGoal.user_id == user_id, FinancialGoal.status == GoalStatus.ACTIVE, FinancialGoal.target_date.is_not(None))).all()
    for goal in goals:
        days = (goal.target_date - today).days
        if days < 0:
            yield (AlertType.GOAL_DEADLINE, AlertSeverity.CRITICAL, f"{goal.name} deadline passed", f"Goal deadline was {goal.target_date}. Review the remaining target.", goal.id)
        elif days <= 7:
            yield (AlertType.GOAL_DEADLINE, AlertSeverity.WARNING, f"{goal.name} deadline is near", f"Goal deadline is in {days} day(s), on {goal.target_date}.", goal.id)

@router.get("", response_model=list[AlertResponse])
def list_alerts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(FinancialAlert).where(FinancialAlert.user_id == user.id).order_by(FinancialAlert.is_read, FinancialAlert.created_at.desc())).all()

@router.get("/summary", response_model=AlertSummary)
def alert_summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = list(_alerts(db, user.id))
    return AlertSummary(total=len(rows), unread=len(rows), critical=sum(x[1] == AlertSeverity.CRITICAL for x in rows), warning=sum(x[1] == AlertSeverity.WARNING for x in rows), info=sum(x[1] == AlertSeverity.INFO for x in rows))

@router.post("/refresh", response_model=list[AlertResponse])
def refresh_alerts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    existing = db.scalars(select(FinancialAlert).where(FinancialAlert.user_id == user.id)).all()
    for alert in existing:
        db.delete(alert)
    db.flush()
    created = []
    for typ, severity, title, message, ref_id in _alerts(db, user.id):
        alert = FinancialAlert(user_id=user.id, alert_type=typ, severity=severity, title=title, message=message, reference_id=ref_id)
        db.add(alert); created.append(alert)
    db.commit()
    for alert in created: db.refresh(alert)
    return created

@router.patch("/{alert_id}/read")
def mark_read(alert_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    alert = db.scalar(select(FinancialAlert).where(FinancialAlert.id == alert_id, FinancialAlert.user_id == user.id))
    if not alert: raise HTTPException(404, "Alert not found")
    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}
