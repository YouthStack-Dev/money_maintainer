from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.alerts.models import FinancialAlert
from app.budgets.models import Budget
from app.categories.models import Category
from app.core.database import get_db
from app.core.dependencies import current_user
from app.debts.models import Debt, DebtDirection, DebtStatus
from app.goals.models import FinancialGoal, GoalStatus
from app.office_reimbursements.models import OfficeReimbursement, OfficeReimbursementStatus
from app.personal_finance_home.schemas import MoneyHomeResponse
from app.transactions.models import Transaction, TransactionType
from app.users.models import User

router = APIRouter()


def _money(value):
    return Decimal(value or 0)


def _transactions(db, user_id, start, end):
    return db.scalars(select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.is_active.is_(True),
        Transaction.transaction_date >= datetime.combine(start, time.min),
        Transaction.transaction_date < datetime.combine(end + timedelta(days=1), time.min),
    ).order_by(Transaction.transaction_date.desc(), Transaction.id.desc())).all()


@router.get("", response_model=MoneyHomeResponse)
def personal_finance_home(user: User = Depends(current_user), db: Session = Depends(get_db)):
    today = date.today()
    month_start = today.replace(day=1)
    txs = _transactions(db, user.id, month_start, today)

    income = sum((_money(t.amount) for t in txs if t.transaction_type == TransactionType.INCOME), Decimal("0"))
    refunds = sum((_money(t.amount) for t in txs if t.transaction_type == TransactionType.REFUND), Decimal("0"))
    spending = sum((_money(t.amount) for t in txs if t.transaction_type == TransactionType.EXPENSE), Decimal("0"))

    accounts = db.scalars(select(Account).where(
        Account.user_id == user.id, Account.is_active.is_(True),
        Account.account_type != AccountType.CREDIT_CARD,
    )).all()
    account_ids = [a.id for a in accounts]
    balances = {a.id: _money(a.opening_balance) for a in accounts}
    all_account_ids = [a.id for a in db.scalars(select(Account).where(
        Account.user_id == user.id, Account.is_active.is_(True)
    )).all()]
    if all_account_ids:
        rows = db.scalars(select(Transaction).where(
            Transaction.user_id == user.id,
            Transaction.is_active.is_(True),
            Transaction.account_id.in_(all_account_ids),
        )).all()
        for tx in rows:
            amount = _money(tx.amount)
            if tx.account_id in balances:
                if tx.transaction_type in (TransactionType.INCOME, TransactionType.REFUND):
                    balances[tx.account_id] += amount
                elif tx.transaction_type in (TransactionType.EXPENSE, TransactionType.TRANSFER):
                    balances[tx.account_id] -= amount
            if tx.transaction_type == TransactionType.TRANSFER and tx.transfer_account_id in balances:
                balances[tx.transfer_account_id] += amount
    available = sum(balances.values(), Decimal("0"))

    categories = {c.id: c.name for c in db.scalars(select(Category).where(Category.user_id == user.id)).all()}
    by_category = defaultdict(Decimal)
    for tx in txs:
        if tx.transaction_type == TransactionType.EXPENSE:
            by_category[categories.get(tx.category_id, "Uncategorized")] += _money(tx.amount)
    top_categories = [{"category": n, "amount": a} for n, a in sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]]

    budgets = db.scalars(select(Budget).where(
        Budget.user_id == user.id,
        Budget.is_active.is_(True),
        Budget.period_start <= datetime.combine(today, time.max),
        Budget.period_end >= datetime.combine(today, time.min),
    )).all()
    budget_spent = defaultdict(Decimal)
    for tx in txs:
        if tx.transaction_type == TransactionType.EXPENSE:
            budget_spent[tx.category_id] += _money(tx.amount)
    budget_total = sum((_money(b.amount) for b in budgets), Decimal("0"))
    spent = sum((budget_spent[b.category_id] for b in budgets), Decimal("0"))

    lent = db.scalars(select(Debt).where(
        Debt.user_id == user.id, Debt.direction == DebtDirection.LENT,
        Debt.status != DebtStatus.CANCELLED, Debt.outstanding_amount > 0,
    )).all()
    borrowed = db.scalars(select(Debt).where(
        Debt.user_id == user.id, Debt.direction == DebtDirection.BORROWED,
        Debt.status != DebtStatus.CANCELLED, Debt.outstanding_amount > 0,
    )).all()
    money_owed = sum((_money(d.outstanding_amount) for d in lent), Decimal("0"))
    money_user_owes = sum((_money(d.outstanding_amount) for d in borrowed), Decimal("0"))

    from app.credit_cards.router import _summary
    cards = db.scalars(select(Account).where(
        Account.user_id == user.id, Account.account_type == AccountType.CREDIT_CARD,
        Account.is_active.is_(True),
    )).all()
    card_outstanding = Decimal("0")
    for card in cards:
        if card.credit_limit is not None and card.statement_day is not None and card.payment_due_day is not None:
            card_outstanding += max(Decimal("0"), _money(_summary(db, user.id, card).outstanding_balance))

    pending_reimbursements = db.scalars(select(OfficeReimbursement).where(
        OfficeReimbursement.user_id == user.id,
        OfficeReimbursement.status == OfficeReimbursementStatus.PENDING,
    )).all()
    office_pending = sum((_money(r.amount) for r in pending_reimbursements), Decimal("0"))

    goals = db.scalars(select(FinancialGoal).where(
        FinancialGoal.user_id == user.id, FinancialGoal.status == GoalStatus.ACTIVE,
    )).all()
    near_deadline = sum(1 for g in goals if g.target_date and today <= g.target_date <= today + timedelta(days=7))

    overdue = [d for d in borrowed + lent if d.due_date and d.due_date < today]
    upcoming = [d for d in borrowed + lent if d.due_date and today <= d.due_date <= today + timedelta(days=7)]
    obligations = [
        {"type": "DEBT", "person": d.person_name, "amount": _money(d.outstanding_amount), "due_date": d.due_date}
        for d in sorted(overdue + upcoming, key=lambda d: d.due_date)[:5]
    ]

    unread_alerts = db.scalar(select(func.count(FinancialAlert.id)).where(
        FinancialAlert.user_id == user.id, FinancialAlert.is_read.is_(False)
    )) or 0

    recent = [
        {"id": t.id, "type": t.transaction_type.value, "amount": _money(t.amount),
         "description": t.description, "date": t.transaction_date}
        for t in txs[:5]
    ]

    return MoneyHomeResponse(
        as_of=today,
        available_money=available,
        current_month_spending=spending,
        current_month_income=income,
        current_month_refunds=refunds,
        current_month_net_cash_flow=income + refunds - spending,
        budget_total=budget_total,
        budget_spent=spent,
        budget_remaining=budget_total - spent,
        credit_card_outstanding=card_outstanding,
        money_owed_to_user=money_owed,
        money_user_owes=money_user_owes,
        office_reimbursement_pending=office_pending,
        active_goal_count=len(goals),
        goals_near_deadline=near_deadline,
        overdue_debt_count=len(overdue),
        upcoming_debt_count=len(upcoming),
        unread_alert_count=int(unread_alerts),
        top_spending_categories=top_categories,
        upcoming_obligations=obligations,
        recent_activity=recent,
    )
