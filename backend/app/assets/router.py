from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assets.models import Asset
from app.assets.schemas import AssetCreate, AssetResponse, AssetSummary, AssetUpdate
from app.core.database import get_db
from app.core.dependencies import current_user
from app.users.models import User

router = APIRouter()


def _get_asset(db: Session, user_id: int, asset_id: int) -> Asset:
    asset = db.scalar(
        select(Asset).where(Asset.id == asset_id, Asset.user_id == user_id)
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


def _response(asset: Asset) -> AssetResponse:
    purchase = asset.purchase_value
    current = asset.current_value
    appreciation = current - purchase
    return AssetResponse(
        id=asset.id,
        asset_type=asset.asset_type,
        name=asset.name,
        description=asset.description,
        purchase_value=purchase,
        current_value=current,
        currency=asset.currency,
        purchase_date=asset.purchase_date,
        notes=asset.notes,
        is_active=asset.is_active,
        appreciation=appreciation,
        appreciation_percent=(
            (appreciation / purchase * Decimal("100")).quantize(Decimal("0.01"))
            if purchase else Decimal("0")
        ),
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.get("", response_model=list[AssetResponse])
def list_assets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    assets = db.scalars(
        select(Asset)
        .where(Asset.user_id == user.id, Asset.is_active.is_(True))
        .order_by(Asset.name.asc(), Asset.id.asc())
    ).all()
    return [_response(asset) for asset in assets]


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    asset = Asset(user_id=user.id, **payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _response(asset)


@router.get("/summary", response_model=AssetSummary)
def asset_summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    assets = db.scalars(
        select(Asset).where(
            Asset.user_id == user.id, Asset.is_active.is_(True)
        )
    ).all()
    purchase = sum((a.purchase_value for a in assets), Decimal("0"))
    current = sum((a.current_value for a in assets), Decimal("0"))
    appreciation = current - purchase
    return AssetSummary(
        asset_count=len(assets),
        purchase_value=purchase,
        current_value=current,
        appreciation=appreciation,
        appreciation_percent=(
            (appreciation / purchase * Decimal("100")).quantize(Decimal("0.01"))
            if purchase else Decimal("0")
        ),
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _response(_get_asset(db, user.id, asset_id))


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    asset = _get_asset(db, user.id, asset_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return _response(asset)


@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    asset = _get_asset(db, user.id, asset_id)
    asset.is_active = False
    db.commit()
    return {"message": "Asset deactivated"}
