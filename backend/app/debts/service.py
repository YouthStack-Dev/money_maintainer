from datetime import datetime, time, timezone
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.accounts.models import Account
from app.debts.models import Debt, DebtDirection, DebtRepayment, DebtStatus
from app.transactions.models import Transaction, TransactionType

def create_debt(db: Session, user_id: int, values: dict) -> Debt:
    account = db.scalar(select(Account).where(Account.id == values["account_id"], Account.user_id == user_id, Account.is_active.is_(True)))
    if not account:
        raise ValueError("Account not found or inactive")
    amount = values["original_amount"]
    transaction_type = TransactionType.INCOME if values["direction"] == DebtDirection.BORROWED else TransactionType.EXPENSE
    transaction = Transaction(user_id=user_id, account_id=account.id, category_id=None, transfer_account_id=None, transaction_type=transaction_type, amount=amount, description=values.get("description") or f"Debt with {values['person_name']}", transaction_date=datetime.now(timezone.utc))
    db.add(transaction)
    db.flush()
    values = {key: value for key, value in values.items() if key != "account_id"}
    item = Debt(user_id=user_id, outstanding_amount=amount, **values)
    db.add(item); db.commit(); db.refresh(item); return item

def repay_debt(db: Session, user_id: int, debt_id: int, values: dict) -> tuple[Debt, DebtRepayment, Transaction]:
    debt = db.scalar(select(Debt).where(Debt.id == debt_id, Debt.user_id == user_id).with_for_update())
    if not debt: raise ValueError("Debt not found")
    if debt.status in {DebtStatus.SETTLED, DebtStatus.CANCELLED}: raise ValueError("Debt is not open")
    amount = values["amount"]
    if amount > debt.outstanding_amount: raise ValueError("Repayment cannot exceed outstanding amount")
    account = db.scalar(select(Account).where(Account.id == values["account_id"], Account.user_id == user_id, Account.is_active.is_(True)))
    if not account: raise ValueError("Account not found or inactive")
    tx_type = TransactionType.EXPENSE if debt.direction == DebtDirection.BORROWED else TransactionType.INCOME
    tx = Transaction(user_id=user_id, account_id=account.id, category_id=None, transfer_account_id=None,
                     transaction_type=tx_type, amount=amount,
                     description=values.get("note") or f"Debt repayment: {debt.person_name}",
                     transaction_date=datetime.combine(values["repayment_date"], time.min, tzinfo=timezone.utc))
    db.add(tx); db.flush()
    repayment = DebtRepayment(debt_id=debt.id, account_id=account.id, transaction_id=tx.id,
                              amount=amount, repayment_date=values["repayment_date"], note=values.get("note"))
    db.add(repayment)
    debt.outstanding_amount -= amount
    debt.status = DebtStatus.SETTLED if debt.outstanding_amount == 0 else DebtStatus.PARTIALLY_PAID
    db.commit(); db.refresh(debt); db.refresh(repayment); db.refresh(tx)
    return debt, repayment, tx

def list_repayments(db: Session, user_id: int, debt_id: int):
    debt = db.scalar(select(Debt).where(Debt.id == debt_id, Debt.user_id == user_id))
    if not debt: raise ValueError("Debt not found")
    return db.scalars(select(DebtRepayment).where(DebtRepayment.debt_id == debt_id).order_by(DebtRepayment.repayment_date, DebtRepayment.id)).all()

def summary(db: Session, user_id: int):
    rows=db.execute(select(Debt.direction, func.coalesce(func.sum(Debt.outstanding_amount),0), func.count(Debt.id)).where(Debt.user_id==user_id, Debt.status.in_([DebtStatus.ACTIVE,DebtStatus.PARTIALLY_PAID])).group_by(Debt.direction)).all()
    result={DebtDirection.BORROWED:(Decimal("0"),0),DebtDirection.LENT:(Decimal("0"),0)}
    for direction,total,count in rows: result[direction]=(total,count)
    return result
