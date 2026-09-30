import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.debts.models import Debt, DebtRepayment, DebtStatus
from app.categories.models import Category
from app.transactions.models import Transaction
from app.office_reimbursements.models import OfficeReimbursement
from app.corrections.schemas import CorrectionCandidate, CorrectionAction

_CONTEXT = re.compile(
    r"\b(?:that|this|last|latest|previous|recent)\s+(?:transaction|txn|tx)\b"
    r"|\b(?:that|this)\b",
    re.I,
)


def _context_requested(text: str) -> bool:
    return bool(_CONTEXT.search(text))


def _latest_active_transaction(db: Session, user_id: int) -> Transaction | None:
    return db.scalar(
        select(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
        )
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(1)
    )


def build_candidate(db: Session, user_id: int, text: str, today, transaction_id=None):
    from app.corrections.parser import parse_correction

    context_transaction_id = None
    if transaction_id is None and _context_requested(text):
        recent = _latest_active_transaction(db, user_id)
        context_transaction_id = recent.id if recent else None

    parsed = parse_correction(
        text,
        today,
        transaction_id,
        context_transaction_id=context_transaction_id,
    )
    candidate = CorrectionCandidate(**parsed)

    if candidate.account_name:
        accounts = db.scalars(
            select(Account).where(
                Account.user_id == user_id,
                Account.is_active.is_(True),
                Account.name.ilike(candidate.account_name),
            )
        ).all()
        if len(accounts) == 1:
            candidate.account_id = accounts[0].id
        else:
            candidate.missing.append("account")
            candidate.confidence = "MEDIUM"
            candidate.reason = (
                "Choose one active account owned by you."
                if accounts
                else "Choose an active account owned by you."
            )

    if candidate.category_name:
        categories = db.scalars(
            select(Category).where(
                Category.user_id == user_id,
                Category.is_active.is_(True),
                Category.name.ilike(candidate.category_name),
            )
        ).all()
        if len(categories) == 1:
            candidate.category_id = categories[0].id
        else:
            candidate.missing.append("category")
            candidate.confidence = "MEDIUM"
            candidate.reason = "Choose one active category owned by you."

    return candidate


def execute_correction(db: Session, user_id: int, candidate: CorrectionCandidate):
    if candidate.confidence != "HIGH":
        raise ValueError("Correction requires confirmation before saving")
    if candidate.transaction_id is None:
        raise ValueError("Transaction id is required")
    if candidate.action == CorrectionAction.MERGE:
        if candidate.duplicate_transaction_id is None:
            raise ValueError("Duplicate transaction id is required")
        if candidate.duplicate_transaction_id == candidate.transaction_id:
            raise ValueError("Merge requires two distinct transactions")
        target = db.scalar(
            select(Transaction).where(
                Transaction.id == candidate.transaction_id,
                Transaction.user_id == user_id,
                Transaction.is_active.is_(True),
            ).with_for_update()
        )
        duplicate = db.scalar(
            select(Transaction).where(
                Transaction.id == candidate.duplicate_transaction_id,
                Transaction.user_id == user_id,
                Transaction.is_active.is_(True),
            ).with_for_update()
        )
        if not target or not duplicate:
            raise ValueError("Both transactions must exist and belong to you")
        if (
            target.transaction_type != duplicate.transaction_type
            or target.amount != duplicate.amount
            or target.account_id != duplicate.account_id
            or target.category_id != duplicate.category_id
            or target.transfer_account_id != duplicate.transfer_account_id
            or target.transaction_date != duplicate.transaction_date
        ):
            raise ValueError("Only exact duplicate transactions can be safely merged")
        linked = db.scalar(
            select(DebtRepayment).where(
                DebtRepayment.transaction_id.in_([target.id, duplicate.id])
            )
        )
        reimbursement = db.scalar(
            select(OfficeReimbursement).where(
                OfficeReimbursement.user_id == user_id,
                (
                    OfficeReimbursement.expense_transaction_id.in_([target.id, duplicate.id])
                    | OfficeReimbursement.reimbursement_transaction_id.in_([target.id, duplicate.id])
                ),
            )
        )
        if linked or reimbursement:
            raise ValueError("Relationship-linked transactions cannot be merged safely")
        duplicate.is_active = False
        db.commit()
        db.refresh(target)
        return target

    if candidate.action == CorrectionAction.UPDATE and candidate.amount is not None:
        if candidate.amount <= 0:
            raise ValueError("Amount must be greater than zero")

    tx = db.scalar(
        select(Transaction)
        .where(
            Transaction.id == candidate.transaction_id,
            Transaction.user_id == user_id,
        )
        .with_for_update()
    )
    if not tx:
        raise ValueError("Transaction not found")

    repayment = db.scalar(
        select(DebtRepayment)
        .join(Debt, Debt.id == DebtRepayment.debt_id)
        .where(
            DebtRepayment.transaction_id == tx.id,
            Debt.user_id == user_id,
        )
        .with_for_update()
    )
    reimbursement = db.scalar(
        select(OfficeReimbursement).where(
            OfficeReimbursement.user_id == user_id,
            (OfficeReimbursement.expense_transaction_id == tx.id)
            | (OfficeReimbursement.reimbursement_transaction_id == tx.id),
        ).with_for_update()
    )

    if reimbursement is not None:
        raise ValueError(
            "This transaction is linked to an office reimbursement; use reimbursement correction instead"
        )

    if candidate.action == CorrectionAction.DELETE:
        if repayment is not None:
            raise ValueError(
                "A debt repayment cannot be deleted through transaction correction"
            )
        tx.is_active = False
    else:
        if repayment is not None and candidate.amount is not None:
            old_amount = repayment.amount
            new_amount = candidate.amount
            delta = new_amount - old_amount
            debt = db.scalar(
                select(Debt)
                .where(Debt.id == repayment.debt_id, Debt.user_id == user_id)
                .with_for_update()
            )
            if debt is None:
                raise ValueError("Linked debt not found")
            if debt.status == DebtStatus.CANCELLED:
                raise ValueError("Cannot correct a repayment for a cancelled debt")
            new_outstanding = debt.outstanding_amount - delta
            if new_outstanding < 0:
                raise ValueError("Repayment correction cannot exceed the debt outstanding balance")
            debt.outstanding_amount = new_outstanding
            debt.status = (
                DebtStatus.SETTLED
                if new_outstanding == 0
                else (
                    DebtStatus.PARTIALLY_PAID
                    if new_outstanding < debt.original_amount
                    else DebtStatus.ACTIVE
                )
            )
            repayment.amount = new_amount
            tx.amount = new_amount
        elif candidate.amount is not None:
            tx.amount = candidate.amount

        if candidate.transaction_date is not None:
            tx.transaction_date = candidate.transaction_date
            if repayment is not None:
                repayment.repayment_date = candidate.transaction_date.date()
        if candidate.description is not None:
            tx.description = candidate.description

        if candidate.account_id is not None:
            account = db.scalar(
                select(Account).where(
                    Account.id == candidate.account_id,
                    Account.user_id == user_id,
                    Account.is_active.is_(True),
                )
            )
            if not account:
                raise ValueError("Account not found")
            if tx.transaction_type.value == "TRANSFER":
                raise ValueError("Transfer account correction is not supported in this slice")
            tx.account_id = account.id

        if candidate.category_id is not None:
            category = db.scalar(
                select(Category).where(
                    Category.id == candidate.category_id,
                    Category.user_id == user_id,
                    Category.is_active.is_(True),
                )
            )
            if not category:
                raise ValueError("Category not found")
            if tx.transaction_type.value not in {"INCOME", "EXPENSE"}:
                raise ValueError(
                    "Category correction is only supported for income and expense transactions"
                )
            expected_type = "INCOME" if tx.transaction_type.value == "INCOME" else "EXPENSE"
            if category.category_type.value != expected_type:
                raise ValueError(
                    f"Category type must be {expected_type} for this transaction"
                )
            tx.category_id = category.id

    db.commit()
    db.refresh(tx)
    return tx
