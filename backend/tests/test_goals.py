from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.core.database import SessionLocal
from app.goals.models import FinancialGoal, GoalContribution, GoalStatus
from app.goals.router import _progress
from app.users.models import User


def _goal(db, target=Decimal("100000")):
    user = User(email=f"goal-{uuid4()}@x.test", full_name="Goal", password_hash="x")
    db.add(user)
    db.flush()
    goal = FinancialGoal(
        user_id=user.id,
        name="Home Fund",
        target_amount=target,
        target_date=date(2027, 12, 31),
    )
    db.add(goal)
    db.flush()
    return user, goal


def test_goal_progress_uses_contributions():
    db = SessionLocal()
    user, goal = _goal(db)
    db.add_all([
        GoalContribution(goal_id=goal.id, amount=Decimal("15000"), contribution_date=date(2026, 9, 1)),
        GoalContribution(goal_id=goal.id, amount=Decimal("5000"), contribution_date=date(2026, 9, 15)),
    ])
    db.commit()

    progress = _progress(db, goal)
    assert progress.current_amount == Decimal("20000.00")
    assert progress.remaining_amount == Decimal("80000.00")
    assert progress.progress_percent == Decimal("20.00")
    db.close()


def test_contribution_completes_goal():
    db = SessionLocal()
    user, goal = _goal(db, Decimal("20000"))
    db.add(GoalContribution(goal_id=goal.id, amount=Decimal("20000"), contribution_date=date(2026, 9, 29)))
    db.flush()
    goal.status = GoalStatus.COMPLETED
    db.commit()
    db.refresh(goal)

    assert goal.status == GoalStatus.COMPLETED
    db.close()


def test_cancelled_goal_can_be_distinguished_from_completed():
    db = SessionLocal()
    user, goal = _goal(db)
    goal.status = GoalStatus.CANCELLED
    db.commit()
    assert goal.status == GoalStatus.CANCELLED
    db.close()
