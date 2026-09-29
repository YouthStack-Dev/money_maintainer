from datetime import date
from decimal import Decimal
from uuid import uuid4
from app.alerts.models import AlertSeverity, AlertType
from app.alerts.router import _alerts
from app.core.database import SessionLocal
from app.users.models import User

def test_alert_engine_has_expected_types():
    assert AlertType.CREDIT_CARD_DUE.value == "CREDIT_CARD_DUE"
    assert AlertType.DEBT_OVERDUE.value == "DEBT_OVERDUE"
    assert AlertType.GOAL_DEADLINE.value == "GOAL_DEADLINE"
    assert AlertSeverity.CRITICAL.value == "CRITICAL"

def test_alerts_are_user_scoped():
    db=SessionLocal()
    user=User(email=f"alerts-{uuid4()}@x.test",full_name="Alerts",password_hash="x")
    db.add(user); db.commit()
    assert list(_alerts(db,user.id)) == []
    db.close()
