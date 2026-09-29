from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class CreditCardSettingsUpdate(BaseModel):
    credit_limit: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    statement_day: int = Field(ge=1, le=31)
    payment_due_day: int = Field(ge=1, le=31)


class CreditCardSummary(BaseModel):
    account_id: int
    name: str
    institution_name: str | None
    credit_limit: Decimal
    current_balance: Decimal
    outstanding_balance: Decimal
    available_credit: Decimal
    utilization_percent: Decimal
    statement_day: int
    payment_due_day: int
    next_payment_due_date: date
    is_active: bool
