from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.assets.models import AssetType


class AssetCreate(BaseModel):
    asset_type: AssetType
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    purchase_value: Decimal = Field(ge=0, max_digits=20, decimal_places=2)
    current_value: Decimal = Field(ge=0, max_digits=20, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    purchase_date: date | None = None
    notes: str | None = Field(default=None, max_length=500)


class AssetUpdate(BaseModel):
    asset_type: AssetType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    purchase_value: Decimal | None = Field(default=None, ge=0, max_digits=20, decimal_places=2)
    current_value: Decimal | None = Field(default=None, ge=0, max_digits=20, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    purchase_date: date | None = None
    notes: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_type: AssetType
    name: str
    description: str | None
    purchase_value: Decimal
    current_value: Decimal
    currency: str
    purchase_date: date | None
    notes: str | None
    is_active: bool
    appreciation: Decimal
    appreciation_percent: Decimal
    created_at: datetime
    updated_at: datetime


class AssetSummary(BaseModel):
    asset_count: int
    purchase_value: Decimal
    current_value: Decimal
    appreciation: Decimal
    appreciation_percent: Decimal
