from decimal import Decimal

from app.accounts.models import AccountType
from app.accounts.schemas import AccountCreate, AccountUpdate


def test_account_create_defaults():
    account = AccountCreate(name="HDFC Bank", account_type=AccountType.BANK_ACCOUNT)
    assert account.currency == "INR"
    assert account.opening_balance == Decimal("0")


def test_account_create_accepts_opening_balance():
    account = AccountCreate(
        name="Cash",
        account_type=AccountType.CASH,
        opening_balance=Decimal("1250.50"),
    )
    assert account.opening_balance == Decimal("1250.50")


def test_account_update_is_partial():
    update = AccountUpdate(is_active=False)
    assert update.is_active is False
    assert update.name is None
