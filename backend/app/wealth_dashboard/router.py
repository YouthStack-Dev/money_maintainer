from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.assets.models import Asset
from app.cash_flow.models import CashFlowPlan
from app.core.database import get_db
from app.core.dependencies import current_user
from app.debts.models import Debt, DebtStatus
from app.goals.models import FinancialGoal, GoalStatus
from app.investment_transactions.models import InvestmentTransaction
from app.investments.models import InvestmentHolding
from app.net_worth.models import NetWorthSnapshot
from app.net_worth.router import _load_values
from app.users.models import User
from app.wealth_dashboard.schemas import (
    WealthDashboardResponse,
    WealthDashboardTrendPoint,
    WealthDashboardTrendResponse,
)

router = APIRouter()


@router.get("", response_model=WealthDashboardResponse)
def dashboard(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    accounts = db.scalars(select(Account).where(Account.user_id == user.id, Account.is_active.is_(True))).all()
    holdings = db.scalars(select(InvestmentHolding).where(InvestmentHolding.user_id == user.id, InvestmentHolding.is_active.is_(True))).all()
    assets = db.scalars(select(Asset).where(Asset.user_id == user.id, Asset.is_active.is_(True))).all()
    debts = db.scalars(select(Debt).where(Debt.user_id == user.id, Debt.status != DebtStatus.CANCELLED)).all()
    goals = db.scalars(select(FinancialGoal).where(FinancialGoal.user_id == user.id, FinancialGoal.status == GoalStatus.ACTIVE)).all()
    plans = db.scalars(select(CashFlowPlan).where(CashFlowPlan.user_id == user.id, CashFlowPlan.is_active.is_(True))).all()
    investment_transactions = db.scalars(select(InvestmentTransaction).where(InvestmentTransaction.user_id == user.id)).all()

    live = _load_values(db, user.id)
    latest = db.scalars(
        select(NetWorthSnapshot)
        .where(NetWorthSnapshot.user_id == user.id)
        .order_by(NetWorthSnapshot.snapshot_date.desc(), NetWorthSnapshot.id.desc())
        .limit(1)
    ).first()

    liquid_assets = live["liquid_assets"]
    credit_card_debt = live["credit_card_debt"]
    other_assets = live["other_assets"]
    lent_receivables = live["lent_receivables"]
    borrowed_debt = live["borrowed_debt"]
    total_assets = live["total_assets"]
    total_liabilities = live["total_liabilities"]
    net_worth = live["net_worth"]

    investment_value = sum((h.market_value for h in holdings), Decimal("0"))
        total_assets = liquid_assets + investment_value + other_assets + lent_receivables
        total_liabilities = credit_card_debt + borrowed_debt
        net_worth = total_assets - total_liabilities

    investment_value = sum((h.market_value for h in holdings), Decimal("0"))
    investment_invested = sum((h.invested_value for h in holdings), Decimal("0"))
    unrealized = investment_value - investment_invested
    realized = sum((tx.realized_gain_loss or Decimal("0") for tx in investment_transactions), Decimal("0"))
    total_return = realized + unrealized
    return_percent = (total_return / investment_invested * Decimal("100")).quantize(Decimal("0.01")) if investment_invested else Decimal("0")

    today = date.today()
    overdue = sum(1 for d in debts if d.due_date and d.due_date < today and d.outstanding_amount > 0)
    upcoming = sum(1 for d in debts if d.due_date and today <= d.due_date <= today + timedelta(days=3) and d.outstanding_amount > 0)
    goals_near = sum(1 for g in goals if g.target_date and today <= g.target_date <= today + timedelta(days=7))

    previous = db.scalars(
        select(NetWorthSnapshot)
        .where(NetWorthSnapshot.user_id == user.id)
        .order_by(NetWorthSnapshot.snapshot_date.desc(), NetWorthSnapshot.id.desc())
        .offset(1).limit(1)
    ).first()
    change = (latest.net_worth - previous.net_worth) if latest and previous else None
    change_percent = (
        (change / previous.net_worth * Decimal("100")).quantize(Decimal("0.01"))
        if change is not None and previous and previous.net_worth else None
    )

    return WealthDashboardResponse(
        as_of=today,
        net_worth=net_worth,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        liquid_assets=liquid_assets,
        investment_value=investment_value,
        other_assets=other_assets,
        lent_receivables=lent_receivables,
        credit_card_debt=credit_card_debt,
        borrowed_debt=borrowed_debt,
        investment_invested_value=investment_invested,
        investment_unrealized_gain_loss=unrealized,
        investment_realized_gain_loss=realized,
        investment_total_return=total_return,
        investment_return_percent=return_percent,
        account_count=len(accounts),
        investment_holding_count=len(holdings),
        asset_count=len(assets),
        active_debt_count=len(debts),
        overdue_debt_count=overdue,
        upcoming_debt_count=upcoming,
        active_goal_count=len(goals),
        goals_near_deadline_count=goals_near,
        active_cash_flow_plan_count=len(plans),
        net_worth_change=change,
        net_worth_change_percent=change_percent,
    )


@router.get("/trend", response_model=WealthDashboardTrendResponse)
def trend(
    limit: int = 12,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 120))
    snapshots = db.scalars(
        select(NetWorthSnapshot)
        .where(NetWorthSnapshot.user_id == user.id)
        .order_by(NetWorthSnapshot.snapshot_date.desc(), NetWorthSnapshot.id.desc())
        .limit(limit)
    ).all()
    return WealthDashboardTrendResponse(
        points=[
            WealthDashboardTrendPoint(
                snapshot_date=s.snapshot_date,
                net_worth=s.net_worth,
                total_assets=s.total_assets,
                total_liabilities=s.total_liabilities,
            )
            for s in reversed(snapshots)
        ]
    )
