from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.categories.models import CategoryType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category_type: CategoryType
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    parent_id: int | None = None
    category_type: CategoryType | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category_type: CategoryType
    parent_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
