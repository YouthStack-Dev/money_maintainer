from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InvestmentType(str, Enum):
    STOCK = "STOCK"
    MUTUAL_FUND = "MUTUAL_FUND"
    ETF = "ETF"
    BOND = "BOND"
    CRYPTO = "CRYPTO"
    OTHER = "OTHER"


class InvestmentHolding(Base):
    __tablename__ = "investment_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    investment_type: Mapped[InvestmentType] = mapped_column(
        SAEnum(InvestmentType, name="investment_type"), nullable=False, index=True
    )
    symbol: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    average_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="INR")
    notes: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def invested_value(self) -> Decimal:
        return self.quantity * self.average_cost

    @property
    def market_value(self) -> Decimal:
        return self.quantity * self.current_price

    @property
    def unrealized_gain_loss(self) -> Decimal:
        return self.market_value - self.invested_value
