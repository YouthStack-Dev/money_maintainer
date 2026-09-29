from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from app.transactions.models import TransactionType


class QuickEntryConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class QuickEntryStatus(str, Enum):
    SAVED = "SAVED"
    PARTIAL = "PARTIAL"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"


class QuickEntryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class QuickEntryCandidate(BaseModel):
    text: str
    transaction_type: TransactionType | None = None
    amount: Decimal | None = None
    description: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    account_id: int | None = None
    account_name: str | None = None
    transaction_date: datetime | None = None
    confidence: QuickEntryConfidence
    missing: list[str] = Field(default_factory=list)
    reason: str | None = None


class QuickEntryResponse(BaseModel):
    status: QuickEntryStatus
    candidates: list[QuickEntryCandidate]
    transaction_ids: list[int] = Field(default_factory=list)
