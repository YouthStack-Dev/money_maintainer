from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.office_reimbursements.models import OfficeReimbursement, OfficeReimbursementStatus
from app.office_reimbursements.schemas import OfficeReimbursementCreate, OfficeReimbursementResponse
from app.transactions.models import Transaction, TransactionType
from app.accounts.models import Account
from app.users.models import User

router = APIRouter()

@router.get("", response_model=list[OfficeReimbursementResponse])
def list_office_reimbursements(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(OfficeReimbursement).where(OfficeReimbursement.user_id == user.id).order_by(OfficeReimbursement.id.desc())).all()

@router.post("", response_model=OfficeReimbursementResponse)
def create_office_reimbursement(payload: OfficeReimbursementCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    tx = db.scalar(select(Transaction).where(Transaction.id == payload.expense_transaction_id, Transaction.user_id == user.id, Transaction.is_active.is_(True)))
    if not tx or tx.transaction_type != TransactionType.EXPENSE:
        raise HTTPException(status_code=400, detail="An active expense transaction is required")
    existing = db.scalar(select(OfficeReimbursement).where(OfficeReimbursement.expense_transaction_id == tx.id))
    if existing:
        raise HTTPException(status_code=409, detail="Transaction is already marked for office reimbursement")
    item = OfficeReimbursement(user_id=user.id, expense_transaction_id=tx.id, amount=tx.amount, description=payload.description)
    db.add(item); db.commit(); db.refresh(item); return item

@router.post("/{reimbursement_id}/reimburse", response_model=OfficeReimbursementResponse)
def reimburse(reimbursement_id: int, account_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(OfficeReimbursement).where(OfficeReimbursement.id == reimbursement_id, OfficeReimbursement.user_id == user.id).with_for_update())
    if not item: raise HTTPException(status_code=404, detail="Office reimbursement not found")
    if item.status != OfficeReimbursementStatus.PENDING: raise HTTPException(status_code=400, detail="Office reimbursement is not pending")
    account = db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user.id, Account.is_active.is_(True)))
    if not account: raise HTTPException(status_code=400, detail="Account not found or inactive")
    tx = Transaction(user_id=user.id, account_id=account_id, category_id=None, transfer_account_id=None, transaction_type=TransactionType.REFUND, amount=item.amount, description=f"Office reimbursement: {item.description}", transaction_date=item.created_at)
    db.add(tx); db.flush()
    item.reimbursement_transaction_id = tx.id
    item.status = OfficeReimbursementStatus.REIMBURSED
    db.commit(); db.refresh(item); return item
