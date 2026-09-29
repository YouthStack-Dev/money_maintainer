from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.debts.models import DebtDirection, DebtStatus

class DebtCreate(BaseModel):
    direction: DebtDirection
    person_name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    original_amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    due_date: date | None = None

class DebtUpdate(BaseModel):
    person_name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    due_date: date | None = None
    status: DebtStatus | None = None

class DebtResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    direction: DebtDirection
    person_name: str
    description: str | None
    original_amount: Decimal
    outstanding_amount: Decimal
    due_date: date | None
    status: DebtStatus
    created_at: datetime
    updated_at: datetime

class DebtRepaymentCreate(BaseModel):
    account_id: int
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    repayment_date: date
    note: str | None = None

class DebtRepaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    debt_id: int
    account_id: int
    transaction_id: int
    amount: Decimal
    repayment_date: date
    note: str | None
    created_at: datetime

class DebtSummary(BaseModel):
    total_borrowed_outstanding: Decimal
    total_lent_outstanding: Decimal
    active_borrowed_count: int
    active_lent_count: int
