from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class DebtDirection(str, Enum):
    BORROWED = "BORROWED"
    LENT = "LENT"

class DebtStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"

class Debt(Base):
    __tablename__ = "debts"
    __table_args__ = (
        CheckConstraint("original_amount > 0", name="ck_debt_original_positive"),
        CheckConstraint("outstanding_amount >= 0", name="ck_debt_outstanding_nonnegative"),
        CheckConstraint("outstanding_amount <= original_amount", name="ck_debt_outstanding_lte_original"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    direction: Mapped[DebtDirection] = mapped_column(SAEnum(DebtDirection, name="debt_direction"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    person_name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    original_amount: Mapped[Decimal] = mapped_column(Numeric(15,2), nullable=False)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(15,2), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[DebtStatus] = mapped_column(SAEnum(DebtStatus, name="debt_status"), nullable=False, default=DebtStatus.ACTIVE, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DebtRepayment(Base):
    __tablename__ = "debt_repayments"
    __table_args__ = (
        UniqueConstraint("debt_id", "transaction_id", name="uq_debt_repayment_transaction"),
        CheckConstraint("amount > 0", name="ck_debt_repayment_positive"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    debt_id: Mapped[int] = mapped_column(ForeignKey("debts.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15,2), nullable=False)
    repayment_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
