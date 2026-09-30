from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.office_reimbursements.models import OfficeReimbursementStatus

class OfficeReimbursementCreate(BaseModel):
    expense_transaction_id: int
    description: str = Field(min_length=1, max_length=500)

class OfficeReimbursementResponse(BaseModel):
    id: int
    expense_transaction_id: int
    reimbursement_transaction_id: int | None
    amount: Decimal
    description: str
    status: OfficeReimbursementStatus
    created_at: datetime
    updated_at: datetime
