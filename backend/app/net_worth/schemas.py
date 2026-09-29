from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class NetWorthSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    snapshot_date: date
    liquid_assets: Decimal
    investment_value: Decimal
    other_assets: Decimal
    lent_receivables: Decimal
    credit_card_debt: Decimal
    borrowed_debt: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    created_at: datetime
    updated_at: datetime


class NetWorthCurrentResponse(BaseModel):
    snapshot_date: date
    liquid_assets: Decimal
    investment_value: Decimal
    other_assets: Decimal
    lent_receivables: Decimal
    credit_card_debt: Decimal
    borrowed_debt: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal


class NetWorthSnapshotGenerate(BaseModel):
    snapshot_date: date | None = None
