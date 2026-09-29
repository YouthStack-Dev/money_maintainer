from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.categories.models import Category
from app.core.database import get_db
from app.core.dependencies import current_user
from app.transactions.models import Transaction, TransactionType
from app.transactions.schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from app.users.models import User

router = APIRouter()


def _get_transaction(db: Session, transaction_id: int, user_id: int) -> Transaction:
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


def _validate_references(
    db: Session,
    user_id: int,
    account_id: int,
    category_id: int | None,
    transfer_account_id: int | None,
    transaction_type: TransactionType,
) -> None:
    account = db.scalar(
        select(Account).where(Account.id == account_id, Account.user_id == user_id, Account.is_active.is_(True))
    )
    if not account:
        raise HTTPException(status_code=400, detail="Account not found")

    if transfer_account_id is not None:
        transfer_account = db.scalar(
            select(Account).where(
                Account.id == transfer_account_id,
                Account.user_id == user_id,
            )
        )
        if not transfer_account:
            raise HTTPException(status_code=400, detail="Transfer account not found")
        if transfer_account.id == account.id:
            raise HTTPException(
                status_code=400,
                detail="Transfer accounts must be different",
            )

    if transaction_type == TransactionType.TRANSFER:
        if transfer_account_id is None or category_id is not None:
            raise HTTPException(status_code=400, detail="Invalid transfer references")
        return

    if transfer_account_id is not None:
        raise HTTPException(status_code=400, detail="Transfer account only applies to transfers")

    if category_id is not None:
        category = db.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.is_active.is_(True),
            )
        )
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")



@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
    ).all()


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _validate_references(
        db,
        user.id,
        payload.account_id,
        payload.category_id,
        payload.transfer_account_id,
        payload.transaction_type,
    )
    transaction = Transaction(user_id=user.id, **payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _get_transaction(db, transaction_id, user.id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    transaction = _get_transaction(db, transaction_id, user.id)
    values = payload.model_dump(exclude_unset=True)

    effective = {
        "account_id": values.get("account_id", transaction.account_id),
        "category_id": values.get("category_id", transaction.category_id),
        "transfer_account_id": values.get(
            "transfer_account_id", transaction.transfer_account_id
        ),
        "transaction_type": values.get(
            "transaction_type", transaction.transaction_type
        ),
    }
    _validate_references(db, user.id, **effective)

    for field, value in values.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    transaction = _get_transaction(db, transaction_id, user.id)
    transaction.is_active = False
    db.commit()
    return {"message": "Transaction deactivated"}
