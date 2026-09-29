from decimal import Decimal

from app.assets.models import Asset, AssetType
from app.assets.router import _response


def test_asset_appreciation():
    asset = Asset(
        user_id=1,
        asset_type=AssetType.PROPERTY,
        name="Farm Land",
        purchase_value=Decimal("1000000"),
        current_value=Decimal("1250000"),
        currency="INR",
        is_active=True,
    )
    response = _response(asset)
    assert response.appreciation == Decimal("250000")
    assert response.appreciation_percent == Decimal("25.00")


def test_asset_depreciation():
    asset = Asset(
        user_id=1,
        asset_type=AssetType.VEHICLE,
        name="Vehicle",
        purchase_value=Decimal("800000"),
        current_value=Decimal("600000"),
        currency="INR",
        is_active=True,
    )
    response = _response(asset)
    assert response.appreciation == Decimal("-200000")
    assert response.appreciation_percent == Decimal("-25.00")


def test_zero_purchase_value_has_zero_percentage():
    asset = Asset(
        user_id=1,
        asset_type=AssetType.OTHER,
        name="Gift",
        purchase_value=Decimal("0"),
        current_value=Decimal("5000"),
        currency="INR",
        is_active=True,
    )
    response = _response(asset)
    assert response.appreciation_percent == Decimal("0")
