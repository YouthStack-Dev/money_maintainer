from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class MoneyHomeResponse(BaseModel):
    as_of: date
    available_money: Decimal
    current_month_spending: Decimal
    current_month_income: Decimal
    current_month_refunds: Decimal
    current_month_net_cash_flow: Decimal
    budget_total: Decimal
    budget_spent: Decimal
    budget_remaining: Decimal
    credit_card_outstanding: Decimal
    money_owed_to_user: Decimal
    money_user_owes: Decimal
    office_reimbursement_pending: Decimal
    active_goal_count: int
    goals_near_deadline: int
    overdue_debt_count: int
    upcoming_debt_count: int
    unread_alert_count: int
    top_spending_categories: list[dict]
    upcoming_obligations: list[dict]
    recent_activity: list[dict]
