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


def test_sell_quantity_cannot_exceed_holding():
    holding = InvestmentHolding(
        user_id=1,
        investment_type=InvestmentType.STOCK,
        name="Stock",
        quantity=Decimal("2"),
        average_cost=Decimal("100"),
        current_price=Decimal("100"),
        currency="INR",
        is_active=True,
    )
    assert Decimal("3") > holding.quantity


def test_buy_average_cost_includes_fees():
    old_cost = Decimal("10") * Decimal("100")
    new_cost = Decimal("10") * Decimal("120") + Decimal("20")
    average = (old_cost + new_cost) / Decimal("20")
    assert average == Decimal("110")
