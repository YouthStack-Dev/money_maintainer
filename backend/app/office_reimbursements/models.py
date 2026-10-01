from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class OfficeReimbursementStatus(str, Enum):
    PENDING = "PENDING"
    REIMBURSED = "REIMBURSED"
    CANCELLED = "CANCELLED"

class OfficeReimbursement(Base):
    __tablename__ = "office_reimbursements"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expense_transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=False, unique=True)
    reimbursement_transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=True, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[OfficeReimbursementStatus] = mapped_column(SAEnum(OfficeReimbursementStatus, name="office_reimbursement_status"), nullable=False, default=OfficeReimbursementStatus.PENDING, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
