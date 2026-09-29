from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.transactions.models import TransactionType


class TransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None
    transfer_account_id: int | None = None
    transaction_type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    description: str | None = None
    transaction_date: datetime

    @model_validator(mode="after")
    def validate_type(self):
        if self.transaction_type == TransactionType.TRANSFER:
            if self.transfer_account_id is None:
                raise ValueError("transfer_account_id is required for transfers")
            if self.category_id is not None:
                raise ValueError("category_id is not allowed for transfers")
        elif self.transfer_account_id is not None:
            raise ValueError("transfer_account_id is only allowed for transfers")
        return self


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    transfer_account_id: int | None = None
    transaction_type: TransactionType | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=15, decimal_places=2)
    description: str | None = None
    transaction_date: datetime | None = None
    is_active: bool | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    category_id: int | None
    transfer_account_id: int | None
    transaction_type: TransactionType
    amount: Decimal
    description: str | None
    transaction_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
