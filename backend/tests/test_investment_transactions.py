from datetime import datetime, timezone
from decimal import Decimal

from app.investments.models import InvestmentHolding, InvestmentType
from app.investment_transactions.models import InvestmentTransaction, InvestmentTransactionType
from app.investment_transactions.router import _realized_gain


def test_buy_and_sell_realized_gain():
    holding = InvestmentHolding(
        user_id=1,
        investment_type=InvestmentType.STOCK,
        name="Stock",
        quantity=Decimal("10"),
        average_cost=Decimal("100"),
        current_price=Decimal("120"),
        currency="INR",
        is_active=True,
    )
    sell = InvestmentTransaction(
        user_id=1,
        holding_id=1,
        transaction_type=InvestmentTransactionType.SELL,
        quantity=Decimal("4"),
        price=Decimal("130"),
        fees=Decimal("5"),
        transaction_date=datetime.now(timezone.utc),
    )
    assert _realized_gain(sell, holding) == Decimal("115")


def test_buy_cash_value_includes_fees():
    buy = InvestmentTransaction(
        user_id=1,
        holding_id=1,
        transaction_type=InvestmentTransactionType.BUY,
        quantity=Decimal("10"),
        price=Decimal("100"),
        fees=Decimal("12"),
        transaction_date=datetime.now(timezone.utc),
    )
    assert buy.cash_value == Decimal("1012")
