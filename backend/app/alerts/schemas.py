from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.alerts.models import AlertSeverity, AlertType

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    reference_id: int | None
    is_read: bool
    created_at: datetime

class AlertSummary(BaseModel):
    total: int
    unread: int
    critical: int
    warning: int
    info: int
