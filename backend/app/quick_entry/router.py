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
    status = QuickEntryStatus.SAVED if transaction_ids else QuickEntryStatus.NEEDS_CONFIRMATION
    return QuickEntryResponse(
        status=status,
        candidates=candidates,
        transaction_ids=transaction_ids,
    )
