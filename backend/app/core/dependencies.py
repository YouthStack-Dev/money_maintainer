from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from app.core.database import get_db
from app.core.security import decode_token
from app.users.models import User,Role
from app.permissions.service import has_permission

bearer=HTTPBearer(auto_error=False)

def current_user(c: HTTPAuthorizationCredentials=Depends(bearer),db: Session=Depends(get_db)):
    if not c: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Authentication required")
    try:
        p=decode_token(c.credentials); user=db.get(User,int(p["sub"]))
    except (jwt.PyJWTError,KeyError,ValueError,TypeError):
        user=None
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid or inactive account")
    return user

def admin_user(user: User=Depends(current_user), db: Session=Depends(get_db)):
    if user.role not in {Role.ADMIN,Role.SUPER_ADMIN} or not has_permission(db,user,"admins.read"):
        raise HTTPException(status.HTTP_403_FORBIDDEN,"Admin access required")
    return user

def super_admin(user: User=Depends(current_user), db: Session=Depends(get_db)):
    if user.role != Role.SUPER_ADMIN or not has_permission(db,user,"admins.create"):
        raise HTTPException(status.HTTP_403_FORBIDDEN,"Super admin access required")
    return user
