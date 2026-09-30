from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import current_user
from app.corrections.schemas import CorrectionRequest, CorrectionResponse
from app.corrections.service import build_candidate, execute_correction
from app.users.models import User

router = APIRouter()

@router.post("", response_model=CorrectionResponse)
def correct_transaction(payload: CorrectionRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    candidate = build_candidate(db, user.id, payload.text, datetime.now(timezone.utc).date(), payload.transaction_id)
    if payload.confirm:
        if payload.candidate is None:
            raise HTTPException(status_code=400, detail="candidate is required when confirm=true")
        if payload.candidate.text != payload.text:
            raise HTTPException(status_code=400, detail="candidate text must match request text")
        if payload.candidate.missing:
            raise HTTPException(status_code=400, detail="candidate still has missing fields")
        candidate = payload.candidate
        candidate.confidence = "HIGH"
    if candidate.confidence != "HIGH":
        return CorrectionResponse(status="NEEDS_CONFIRMATION", candidate=candidate)
    try:
        tx = execute_correction(db, user.id, candidate)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CorrectionResponse(status="CORRECTED", candidate=candidate, transaction_id=tx.id)
