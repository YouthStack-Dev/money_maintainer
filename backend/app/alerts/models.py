from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class AlertType(str, Enum):
    CREDIT_CARD_DUE = "CREDIT_CARD_DUE"
    CREDIT_CARD_OVER_LIMIT = "CREDIT_CARD_OVER_LIMIT"
    DEBT_DUE = "DEBT_DUE"
    DEBT_OVERDUE = "DEBT_OVERDUE"
    GOAL_DEADLINE = "GOAL_DEADLINE"
    CASH_FLOW_LOW = "CASH_FLOW_LOW"

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class FinancialAlert(Base):
    __tablename__ = "financial_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type: Mapped[AlertType] = mapped_column(SAEnum(AlertType, name="financial_alert_type"), nullable=False, index=True)
    severity: Mapped[AlertSeverity] = mapped_column(SAEnum(AlertSeverity, name="financial_alert_severity"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reference_id: Mapped[int | None] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
