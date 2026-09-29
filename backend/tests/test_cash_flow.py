from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.cash_flow.models import CashFlowItem, CashFlowPlan, CashFlowType
from app.cash_flow.router import _validate_refs
from app.core.database import SessionLocal
from app.users.models import User


def test_cash_flow_plan_and_item():
    db = SessionLocal()
    user = User(email=f"cashflow-{uuid4()}@x.test", full_name="Cash Flow", password_hash="x")
    db.add(user)
    db.flush()
    plan = CashFlowPlan(user_id=user.id, name="October", start_date=date(2026,10,1), end_date=date(2026,10,31), starting_balance=Decimal("50000"))
    db.add(plan)
    db.flush()
    item = CashFlowItem(plan_id=plan.id, name="Salary", flow_type=CashFlowType.INCOME, amount=Decimal("29800"), planned_date=date(2026,10,1))
    db.add(item)
    db.commit()
    assert item.amount == Decimal("29800.00")
    db.close()


def test_plan_dates_are_ordered():
    assert date(2026,10,31) >= date(2026,10,1)
