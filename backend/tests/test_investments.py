from decimal import Decimal

from app.investments.models import InvestmentHolding, InvestmentType
from app.investments.router import _response


def test_investment_valuation():
    holding = InvestmentHolding(
        user_id=1,
        investment_type=InvestmentType.STOCK,
        symbol="ABC",
        name="ABC Ltd",
        quantity=Decimal("10"),
        average_cost=Decimal("100"),
        current_price=Decimal("125"),
        currency="INR",
        is_active=True,
    )
    response = _response(holding)
    assert response.invested_value == Decimal("1000")
    assert response.market_value == Decimal("1250")
    assert response.unrealized_gain_loss == Decimal("250")
    assert response.unrealized_return_percent == Decimal("25.00")


def test_investment_response_supports_loss():
    holding = InvestmentHolding(
        user_id=1,
        investment_type=InvestmentType.MUTUAL_FUND,
        name="Index Fund",
        quantity=Decimal("20"),
        average_cost=Decimal("150"),
        current_price=Decimal("120"),
        currency="INR",
        is_active=True,
    )
    response = _response(holding)
    assert response.unrealized_gain_loss == Decimal("-600")
    assert response.unrealized_return_percent == Decimal("-20.00")
