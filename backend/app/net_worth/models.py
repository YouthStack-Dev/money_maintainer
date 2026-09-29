from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NetWorthSnapshot(Base):
    __tablename__ = "net_worth_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date", name="uq_net_worth_snapshot_user_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    liquid_assets: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    investment_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    other_assets: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    lent_receivables: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    credit_card_debt: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    borrowed_debt: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_assets: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_liabilities: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    net_worth: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
