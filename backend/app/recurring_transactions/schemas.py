from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.recurring_transactions.models import RecurringFrequency
from app.transactions.models import TransactionType


class RecurringTransactionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    account_id: int
    category_id: int | None = None
    transaction_type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    frequency: RecurringFrequency
    start_date: date
    end_date: date | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def validate_dates(self):
        if self.transaction_type == TransactionType.TRANSFER:
            raise ValueError("Recurring transfers are not supported")
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class RecurringTransactionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    account_id: int | None = None
    category_id: int | None = None
    transaction_type: TransactionType | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=15, decimal_places=2)
    frequency: RecurringFrequency | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.transaction_type == TransactionType.TRANSFER:
            raise ValueError("Recurring transfers are not supported")
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class RecurringTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    account_id: int
    category_id: int | None
    transaction_type: TransactionType
    amount: Decimal
    frequency: RecurringFrequency
    start_date: date
    end_date: date | None
    next_run_at: datetime
    last_run_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RecurringTransactionGenerationResponse(BaseModel):
    recurring_transaction_id: int
    transaction_id: int
    scheduled_run_at: datetime
    next_run_at: datetime
    is_active: bool
