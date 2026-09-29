from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.categories.models import Category
from app.categories.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.core.database import get_db
from app.core.dependencies import current_user
from app.users.models import User

router = APIRouter()


def _get_category(db: Session, category_id: int, user_id: int) -> Category:
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def _validate_parent(
    db: Session, parent_id: int | None, user_id: int, category_id: int | None = None
) -> Category | None:
    if parent_id is None:
        return None
    if category_id is not None and parent_id == category_id:
        raise HTTPException(status_code=400, detail="Category cannot be its own parent")

    parent = db.scalar(
        select(Category).where(Category.id == parent_id, Category.user_id == user_id)
    )
    if not parent:
        raise HTTPException(status_code=400, detail="Parent category not found")
    return parent


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Category).where(Category.user_id == user.id).order_by(Category.id)
    ).all()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _validate_parent(db, payload.parent_id, user.id)
    category = Category(user_id=user.id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _get_category(db, category_id, user.id)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    category = _get_category(db, category_id, user.id)
    values = payload.model_dump(exclude_unset=True)

    if "parent_id" in values:
        _validate_parent(db, values["parent_id"], user.id, category.id)

    for field, value in values.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    category = _get_category(db, category_id, user.id)
    category.is_active = False
    db.commit()
    return {"message": "Category deactivated"}
