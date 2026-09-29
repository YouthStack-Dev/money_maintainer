from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.investments.models import InvestmentType


class InvestmentCreate(BaseModel):
    investment_type: InvestmentType
    symbol: str | None = Field(default=None, max_length=40)
    name: str = Field(min_length=1, max_length=160)
    quantity: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    average_cost: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    current_price: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=500)


class InvestmentUpdate(BaseModel):
    investment_type: InvestmentType | None = None
    symbol: str | None = Field(default=None, max_length=40)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    quantity: Decimal | None = Field(default=None, gt=0, max_digits=20, decimal_places=8)
    average_cost: Decimal | None = Field(default=None, gt=0, max_digits=20, decimal_places=8)
    current_price: Decimal | None = Field(default=None, gt=0, max_digits=20, decimal_places=8)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class InvestmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    investment_type: InvestmentType
    symbol: str | None
    name: str
    quantity: Decimal
    average_cost: Decimal
    current_price: Decimal
    currency: str
    notes: str | None
    is_active: bool
    invested_value: Decimal
    market_value: Decimal
    unrealized_gain_loss: Decimal
    unrealized_return_percent: Decimal
    created_at: datetime
    updated_at: datetime


class InvestmentSummary(BaseModel):
    holding_count: int
    invested_value: Decimal
    market_value: Decimal
    unrealized_gain_loss: Decimal
    unrealized_return_percent: Decimal
