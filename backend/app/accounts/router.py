from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.accounts.schemas import AccountCreate, AccountResponse, AccountUpdate
from app.core.database import get_db
from app.core.dependencies import current_user
from app.users.models import User

router = APIRouter()


@router.get("", response_model=list[AccountResponse])
def list_accounts(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Account).where(Account.user_id == user.id).order_by(Account.id)
    ).all()


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    account = Account(user_id=user.id, **payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    account = db.scalar(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    payload: AccountUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    account = db.scalar(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    account = db.scalar(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_active = False
    db.commit()
    return {"message": "Account deactivated"}
