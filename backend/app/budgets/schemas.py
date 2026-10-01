from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BudgetCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=120)
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    period_start: datetime
    period_end: datetime

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end must be on or after period_start")
        return self


class BudgetUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=15, decimal_places=2)
    period_start: datetime | None = None
    period_end: datetime | None = None
    is_active: bool | None = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    amount: Decimal
    period_start: datetime
    period_end: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
