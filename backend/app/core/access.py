from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.permissions.service import has_permission
from app.users.models import User

RESOURCE_MAP={"users":"users","admins":"admins","accounts":"accounts","categories":"categories","transactions":"transactions","summary":"summary","budgets":"budgets","recurring-transactions":"recurring_transactions","debts":"debts"}
METHOD_ACTION={"GET":"read","POST":"create","PATCH":"update","PUT":"update","DELETE":"delete"}

def authorize_path(db: Session, authorization: str | None, path: str, method: str) -> int | None:
    if not path.startswith("/api/v1/") or path.startswith("/api/v1/auth") or path=="/api/v1/health": return None
    parts=path.split("/")
    if len(parts)<4 or parts[3] not in RESOURCE_MAP: return None
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Authentication required")
    try: user_id=int(decode_token(authorization[7:])["sub"])
    except Exception as exc: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid authentication") from exc
    user=db.get(User,user_id)
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid or inactive account")
    code=f"{RESOURCE_MAP[parts[3]]}.{METHOD_ACTION.get(method, 'read')}"
    if not has_permission(db,user,code): raise HTTPException(status.HTTP_403_FORBIDDEN,"Permission denied")
    return user.id
