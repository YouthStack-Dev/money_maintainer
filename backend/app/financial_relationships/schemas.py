from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

class RelationshipIntent(str, Enum):
    LEND = "LEND"
    BORROW = "BORROW"
    REPAY_BORROWED = "REPAY_BORROWED"
    RECEIVE_LENT_REPAYMENT = "RECEIVE_LENT_REPAYMENT"
    CREDIT_CARD_PURCHASE = "CREDIT_CARD_PURCHASE"
    CREDIT_CARD_PAYMENT = "CREDIT_CARD_PAYMENT"
    SALARY = "SALARY"
    REFUND = "REFUND"
    TRANSFER = "TRANSFER"
    EMI = "EMI"

class RelationshipCandidate(BaseModel):
    text: str
    intent: RelationshipIntent | None = None
    amount: Decimal | None = None
    person_name: str | None = None
    account_id: int | None = None
    account_name: str | None = None
    secondary_account_id: int | None = None
    secondary_account_name: str | None = None
    transaction_date: datetime | None = None
    confidence: str
    missing: list[str] = Field(default_factory=list)
    reason: str | None = None

class RelationshipRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    confirm: bool = False
    candidate: RelationshipCandidate | None = None

class RelationshipResponse(BaseModel):
    status: str
    candidate: RelationshipCandidate
    transaction_id: int | None = None
    debt_id: int | None = None
    repayment_id: int | None = None
