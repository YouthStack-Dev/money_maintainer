from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InvestmentTransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    holding_id: Mapped[int] = mapped_column(
        ForeignKey("investment_holdings.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    transaction_type: Mapped[InvestmentTransactionType] = mapped_column(
        SAEnum(InvestmentTransactionType, name="investment_transaction_type"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, server_default="0")
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    @property
    def gross_value(self) -> Decimal:
        return self.quantity * self.price

    @property
    def cash_value(self) -> Decimal:
        if self.transaction_type == InvestmentTransactionType.BUY:
            return self.gross_value + self.fees
        return self.gross_value - self.fees
