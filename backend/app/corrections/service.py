import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.transactions.models import Transaction
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

    return CorrectionCandidate(
        **parse_correction(
            text,
            today,
            transaction_id,
            context_transaction_id=context_transaction_id,
        )
    )


def execute_correction(db: Session, user_id: int, candidate: CorrectionCandidate):
    if candidate.confidence != "HIGH":
        raise ValueError("Correction requires confirmation before saving")
    if candidate.transaction_id is None:
        raise ValueError("Transaction id is required")
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
    if candidate.action == CorrectionAction.DELETE:
        tx.is_active = False
    else:
        if candidate.amount is not None:
            tx.amount = candidate.amount
        if candidate.transaction_date is not None:
            tx.transaction_date = candidate.transaction_date
        if candidate.description is not None:
            tx.description = candidate.description
    db.commit()
    db.refresh(tx)
    return tx
