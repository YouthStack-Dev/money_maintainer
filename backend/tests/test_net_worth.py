from datetime import date
from decimal import Decimal

from app.accounts.models import Account, AccountType
from app.assets.models import Asset, AssetType
from app.debts.models import Debt, DebtDirection, DebtStatus
from app.investments.models import InvestmentHolding, InvestmentType
from app.net_worth.router import _calculate_values
from app.transactions.models import Transaction, TransactionType


def test_net_worth_calculation_includes_assets_investments_receivables_and_liabilities():
    cash = Account(
        id=1,
        user_id=1,
        name="Bank",
        account_type=AccountType.BANK_ACCOUNT,
        opening_balance=Decimal("100000"),
    )
    investment = InvestmentHolding(
        user_id=1,
        investment_type=InvestmentType.STOCK,
        name="Fund",
        quantity=Decimal("10"),
        average_cost=Decimal("1000"),
        current_price=Decimal("1200"),
        currency="INR",
        is_active=True,
    )
    asset = Asset(
        user_id=1,
        asset_type=AssetType.VEHICLE,
        name="Bike",
        purchase_value=Decimal("80000"),
        current_value=Decimal("70000"),
        currency="INR",
        is_active=True,
    )
    lent = Debt(
        user_id=1,
        direction=DebtDirection.LENT,
        account_id=1,
        person_name="Person",
        original_amount=Decimal("30000"),
        outstanding_amount=Decimal("20000"),
        status=DebtStatus.ACTIVE,
    )
    borrowed = Debt(
        user_id=1,
        direction=DebtDirection.BORROWED,
        account_id=1,
        person_name="Bank",
        original_amount=Decimal("15000"),
        outstanding_amount=Decimal("10000"),
        status=DebtStatus.ACTIVE,
    )

    values = _calculate_values(
        [cash],
        [],
        [investment],
        [asset],
        [lent, borrowed],
    )

    assert values["liquid_assets"] == Decimal("100000")
    assert values["investment_value"] == Decimal("12000")
    assert values["other_assets"] == Decimal("70000")
    assert values["lent_receivables"] == Decimal("20000")
    assert values["credit_card_debt"] == Decimal("0")
    assert values["borrowed_debt"] == Decimal("10000")
    assert values["total_assets"] == Decimal("202000")
    assert values["total_liabilities"] == Decimal("10000")
    assert values["net_worth"] == Decimal("192000")


def test_transfer_does_not_change_total_liquid_assets():
    source = Account(
        id=1,
        user_id=1,
        name="Bank",
        account_type=AccountType.BANK_ACCOUNT,
        opening_balance=Decimal("50000"),
    )
    destination = Account(
        id=2,
        user_id=1,
        name="Wallet",
        account_type=AccountType.WALLET,
        opening_balance=Decimal("0"),
    )
    transfer = Transaction(
        user_id=1,
        account_id=1,
        transfer_account_id=2,
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("10000"),
        is_active=True,
    )

    values = _calculate_values([source, destination], [transfer], [], [], [])

    assert values["liquid_assets"] == Decimal("50000")
    assert values["net_worth"] == Decimal("50000")
