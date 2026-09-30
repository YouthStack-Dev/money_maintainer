from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class CorrectionAction(str, Enum):
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class CorrectionCandidate(BaseModel):
    text: str
    action: CorrectionAction | None = None
    transaction_id: int | None = None
    amount: Decimal | None = None
    transaction_date: datetime | None = None
    description: str | None = None
    account_id: int | None = None
    account_name: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    reason: str | None = None
    confidence: str
    missing: list[str] = Field(default_factory=list)


class CorrectionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    transaction_id: int | None = None
    confirm: bool = False
    candidate: CorrectionCandidate | None = None


class CorrectionResponse(BaseModel):
    status: str
    candidate: CorrectionCandidate
    transaction_id: int | None = None
