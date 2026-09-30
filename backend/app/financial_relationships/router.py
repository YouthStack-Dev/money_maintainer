from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.financial_relationships.schemas import RelationshipRequest, RelationshipResponse
from app.financial_relationships.service import build_candidate, execute_candidate
from app.users.models import User

router = APIRouter()

@router.post("", response_model=RelationshipResponse)
def relationship_entry(payload: RelationshipRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    candidate = build_candidate(db, user.id, payload.text, datetime.now(timezone.utc).date())
    if payload.confirm:
        if payload.candidate is None:
            raise HTTPException(status_code=400, detail="candidate is required when confirm=true")
        candidate = payload.candidate
        if candidate.text != payload.text:
            raise HTTPException(status_code=400, detail="candidate text must match request text")
        if candidate.missing:
            raise HTTPException(status_code=400, detail="candidate still has missing fields")
        candidate.confidence = "HIGH"
    if candidate.confidence != "HIGH":
        return RelationshipResponse(status="NEEDS_CONFIRMATION", candidate=candidate)
    try:
        transaction_id, debt_id, repayment_id = execute_candidate(db, user.id, candidate)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RelationshipResponse(status="SAVED", candidate=candidate, transaction_id=transaction_id, debt_id=debt_id, repayment_id=repayment_id)
