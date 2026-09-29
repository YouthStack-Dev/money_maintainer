from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.accounts.models import AccountType


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    account_type: AccountType
    institution_name: str | None = Field(default=None, max_length=120)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    opening_balance: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    institution_name: str | None = Field(default=None, max_length=120)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    opening_balance: Decimal | None = Field(default=None, max_digits=15, decimal_places=2)
    is_active: bool | None = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    account_type: AccountType
    institution_name: str | None
    currency: str
    opening_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
