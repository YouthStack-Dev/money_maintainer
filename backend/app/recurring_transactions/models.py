from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecurringFrequency(str, Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="uq_recurring_transactions_id_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[object] = mapped_column(Numeric(15, 2), nullable=False)
    frequency: Mapped[RecurringFrequency] = mapped_column(SAEnum(RecurringFrequency, name="recurring_frequency"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    next_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RecurringTransactionRun(Base):
    __tablename__ = "recurring_transaction_runs"
    __table_args__ = (
        UniqueConstraint("recurring_transaction_id", "scheduled_run_at", name="uq_recurring_run_schedule"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recurring_transaction_id: Mapped[int] = mapped_column(
        ForeignKey("recurring_transactions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheduled_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
