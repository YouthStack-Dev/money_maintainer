from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.goals.models import GoalStatus


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    target_amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    target_date: date | None = None


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=15, decimal_places=2)
    target_date: date | None = None
    status: GoalStatus | None = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    target_amount: Decimal
    target_date: date | None
    status: GoalStatus
    current_amount: Decimal
    remaining_amount: Decimal
    progress_percent: Decimal
    created_at: datetime
    updated_at: datetime


class ContributionCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    contribution_date: date
    note: str | None = Field(default=None, max_length=500)


class ContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    amount: Decimal
    contribution_date: date
    note: str | None
    created_at: datetime


class GoalProgress(BaseModel):
    goal_id: int
    target_amount: Decimal
    current_amount: Decimal
    remaining_amount: Decimal
    progress_percent: Decimal
    status: GoalStatus
    target_date: date | None
