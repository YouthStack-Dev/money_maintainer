from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.conversational_finance.parser import parse_query
from app.conversational_finance.schemas import ConversationRequest, ConversationResponse
from app.conversational_finance.service import answer_query
from app.core.database import get_db
from app.core.dependencies import current_user
from app.users.models import User

router = APIRouter()

@router.post("", response_model=ConversationResponse)
def conversational_finance(payload: ConversationRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    parsed = parse_query(payload.text)
    answer, data, context, follow_up = answer_query(db, user, payload.text, payload.context)
    return ConversationResponse(
        status="ANSWERED",
        intent=parsed["intent"],
        answer=answer,
        data=data,
        context=context,
        follow_up=follow_up,
    )
