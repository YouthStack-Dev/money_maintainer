from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.cash_flow.models import CashFlowType


class CashFlowPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    start_date: date
    end_date: date
    starting_balance: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class CashFlowPlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    start_date: date | None = None
    end_date: date | None = None
    starting_balance: Decimal | None = Field(default=None, max_digits=15, decimal_places=2)
    is_active: bool | None = None


class CashFlowItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    flow_type: CashFlowType
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    planned_date: date
    category_id: int | None = None
    account_id: int | None = None
    note: str | None = Field(default=None, max_length=500)


class CashFlowItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    flow_type: CashFlowType | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=15, decimal_places=2)
    planned_date: date | None = None
    category_id: int | None = None
    account_id: int | None = None
    note: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class CashFlowItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int
    name: str
    flow_type: CashFlowType
    amount: Decimal
    planned_date: date
    category_id: int | None
    account_id: int | None
    is_active: bool
    note: str | None
    created_at: datetime


class CashFlowPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start_date: date
    end_date: date
    starting_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CashFlowForecast(BaseModel):
    plan_id: int
    planned_income: Decimal
    planned_expenses: Decimal
    planned_net_cash_flow: Decimal
    projected_ending_balance: Decimal
    actual_income: Decimal
    actual_expenses: Decimal
    actual_net_cash_flow: Decimal
    variance: Decimal
