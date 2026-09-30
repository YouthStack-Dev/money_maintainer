from sqlalchemy import select
from sqlalchemy.orm import Session
from app.transactions.models import Transaction
from app.corrections.schemas import CorrectionCandidate, CorrectionAction

def build_candidate(db: Session, user_id: int, text: str, today, transaction_id=None):
    from app.corrections.parser import parse_correction
    return CorrectionCandidate(**parse_correction(text, today, transaction_id))

def execute_correction(db: Session, user_id: int, candidate: CorrectionCandidate):
    if candidate.confidence != "HIGH":
        raise ValueError("Correction requires confirmation before saving")
    tx = db.scalar(select(Transaction).where(
        Transaction.id == candidate.transaction_id,
        Transaction.user_id == user_id,
    ).with_for_update())
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
