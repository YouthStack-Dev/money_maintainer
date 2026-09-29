from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class WealthDashboardResponse(BaseModel):
    as_of: date
    net_worth: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    liquid_assets: Decimal
    investment_value: Decimal
    other_assets: Decimal
    lent_receivables: Decimal
    credit_card_debt: Decimal
    borrowed_debt: Decimal
    investment_invested_value: Decimal
    investment_unrealized_gain_loss: Decimal
    investment_realized_gain_loss: Decimal
    investment_total_return: Decimal
    investment_return_percent: Decimal
    account_count: int
    investment_holding_count: int
    asset_count: int
    active_debt_count: int
    active_goal_count: int
    overdue_debt_count: int
    upcoming_debt_count: int
    goals_near_deadline_count: int
    active_cash_flow_plan_count: int
    net_worth_change: Decimal | None
    net_worth_change_percent: Decimal | None


class WealthDashboardTrendPoint(BaseModel):
    snapshot_date: date
    net_worth: Decimal
    total_assets: Decimal
    total_liabilities: Decimal


class WealthDashboardTrendResponse(BaseModel):
    points: list[WealthDashboardTrendPoint]
