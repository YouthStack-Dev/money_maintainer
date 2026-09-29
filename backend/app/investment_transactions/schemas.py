from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.investment_transactions.models import InvestmentTransactionType


class InvestmentTransactionCreate(BaseModel):
    holding_id: int
    transaction_type: InvestmentTransactionType
    quantity: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    price: Decimal = Field(gt=0, max_digits=20, decimal_places=8)
    fees: Decimal = Field(default=Decimal("0"), ge=0, max_digits=20, decimal_places=8)
    transaction_date: datetime
    notes: str | None = Field(default=None, max_length=500)


class InvestmentTransactionResponse(BaseModel):
    id: int
    holding_id: int
    transaction_type: InvestmentTransactionType
    quantity: Decimal
    price: Decimal
    fees: Decimal
    transaction_date: datetime
    notes: str | None
    gross_value: Decimal
    cash_value: Decimal
    realized_gain_loss: Decimal | None
    created_at: datetime
