from datetime import datetime,timedelta,timezone
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select,update
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import current_user
from app.core.security import access_token,hash_password,one_time_token,refresh_token,token_hash,verify_password
from app.auth.models import SessionToken,OneTimeToken
from app.users.models import User,Role

router=APIRouter()

def issue(db,user):
    raw=refresh_token()
    db.add(SessionToken(user_id=user.id,refresh_token_hash=token_hash(raw),expires_at=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_expire_days)))
    db.commit()
    return {"access_token":access_token(user.id,user.role.value),"refresh_token":raw,"token_type":"bearer","role":user.role}

def create_one_time(db,user,purpose,hours=24):
    raw=one_time_token()
    db.add(OneTimeToken(user_id=user.id,token_hash=token_hash(raw),purpose=purpose,expires_at=datetime.now(timezone.utc)+timedelta(hours=hours)))
    db.commit()
    return raw

@router.post("/register",status_code=201)
def register(email:str,full_name:str,password:str,db:Session=Depends(get_db)):
    email=email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already registered")
    user=User(email=email,full_name=full_name,password_hash=hash_password(password),role=Role.USER)
    db.add(user);db.commit();db.refresh(user)
    # Delivery adapter is intentionally replaceable with SMTP/provider integration.
    verification_token=create_one_time(db,user,"email_verification")
    return {**issue(db,user),"verification_token":verification_token}

@router.post("/login")
def login(email:str,password:str,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==email.lower()))
    if not user or not user.is_active or not verify_password(password,user.password_hash): raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid credentials")
    return issue(db,user)

@router.post("/refresh")
def refresh(refresh_token_value:str,db:Session=Depends(get_db)):
    s=db.scalar(select(SessionToken).where(SessionToken.refresh_token_hash==token_hash(refresh_token_value)))
    now=datetime.now(timezone.utc)
    if not s or s.revoked_at or s.expires_at<=now: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid refresh token")
    user=db.get(User,s.user_id)
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Inactive account")
    s.revoked_at=now;db.commit()
    return issue(db,user)

@router.post("/logout")
def logout(refresh_token_value:str,db:Session=Depends(get_db)):
    s=db.scalar(select(SessionToken).where(SessionToken.refresh_token_hash==token_hash(refresh_token_value)))
    if s: s.revoked_at=datetime.now(timezone.utc);db.commit()
    return {"message":"Logged out"}

@router.post("/verify-email")
def verify_email(token:str,db:Session=Depends(get_db)):
    row=db.scalar(select(OneTimeToken).where(OneTimeToken.token_hash==token_hash(token),OneTimeToken.purpose=="email_verification"))
    now=datetime.now(timezone.utc)
    if not row or row.used_at or row.expires_at<=now: raise HTTPException(400,"Invalid or expired verification token")
    user=db.get(User,row.user_id);user.is_email_verified=True;row.used_at=now;db.commit()
    return {"message":"Email verified"}

@router.post("/forgot-password")
def forgot_password(email:str,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==email.lower()))
    if not user or not user.is_active: return {"message":"If the account exists, a reset email has been sent"}
    reset_token=create_one_time(db,user,"password_reset",hours=1)
    return {"message":"If the account exists, a reset email has been sent","reset_token":reset_token}

@router.post("/reset-password")
def reset_password(token:str,password:str,db:Session=Depends(get_db)):
    row=db.scalar(select(OneTimeToken).where(OneTimeToken.token_hash==token_hash(token),OneTimeToken.purpose=="password_reset"))
    now=datetime.now(timezone.utc)
    if not row or row.used_at or row.expires_at<=now: raise HTTPException(400,"Invalid or expired reset token")
    user=db.get(User,row.user_id);user.password_hash=hash_password(password);row.used_at=now
    db.execute(update(SessionToken).where(SessionToken.user_id==user.id).values(revoked_at=now))
    db.commit()
    return {"message":"Password reset"}

@router.get("/me")
def me(user:User=Depends(current_user)):
    return {"id":user.id,"email":user.email,"full_name":user.full_name,"role":user.role,"is_email_verified":user.is_email_verified}

@router.post("/change-password")
def change_password(password:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    user.password_hash=hash_password(password);db.execute(update(SessionToken).where(SessionToken.user_id==user.id).values(revoked_at=datetime.now(timezone.utc)));db.commit()
    return {"message":"Password changed"}
