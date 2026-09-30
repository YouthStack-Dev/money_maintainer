from decimal import Decimal

from app.personal_finance_home.schemas import MoneyHomeResponse


def test_personal_finance_home_schema():
    response = MoneyHomeResponse(
        as_of="2026-09-30",
        available_money=Decimal("30000"),
        current_month_spending=Decimal("10000"),
        current_month_income=Decimal("29800"),
        current_month_refunds=Decimal("2000"),
        current_month_net_cash_flow=Decimal("21800"),
        budget_total=Decimal("15000"),
        budget_spent=Decimal("10000"),
        budget_remaining=Decimal("5000"),
        credit_card_outstanding=Decimal("12000"),
        money_owed_to_user=Decimal("40000"),
        money_user_owes=Decimal("10000"),
        office_reimbursement_pending=Decimal("2000"),
        active_goal_count=1,
        goals_near_deadline=0,
        overdue_debt_count=0,
        upcoming_debt_count=1,
        unread_alert_count=2,
        top_spending_categories=[],
        upcoming_obligations=[],
        recent_activity=[],
    )
    assert response.available_money == Decimal("30000")
    assert response.current_month_net_cash_flow == Decimal("21800")
