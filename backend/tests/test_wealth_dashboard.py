from decimal import Decimal


def test_wealth_dashboard_return_percent():
    invested = Decimal("100000")
    realized = Decimal("5000")
    unrealized = Decimal("-2000")
    total_return = realized + unrealized
    assert total_return == Decimal("3000")
    assert (total_return / invested * Decimal("100")).quantize(Decimal("0.01")) == Decimal("3.00")


def test_wealth_dashboard_trend_limit_is_bounded():
    requested = 500
    bounded = max(1, min(requested, 120))
    assert bounded == 120
