from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.quick_entry.schemas import QuickEntryRequest, QuickEntryResponse, QuickEntryStatus
from app.quick_entry.service import build_candidates, save_ready_candidates
from app.users.models import User

router = APIRouter()


@router.post("", response_model=QuickEntryResponse)
def quick_entry(
    payload: QuickEntryRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    candidates = build_candidates(
        db,
        user.id,
        payload.text,
        datetime.now(timezone.utc).date(),
    )
    transaction_ids = save_ready_candidates(db, user.id, candidates)
    db.commit()
    if transaction_ids and any(candidate.confidence != "HIGH" for candidate in candidates):
        status = QuickEntryStatus.PARTIAL
    elif transaction_ids:
        status = QuickEntryStatus.SAVED
    else:
        status = QuickEntryStatus.NEEDS_CONFIRMATION
    return QuickEntryResponse(
        status=status,
        candidates=candidates,
        transaction_ids=transaction_ids,
    )
