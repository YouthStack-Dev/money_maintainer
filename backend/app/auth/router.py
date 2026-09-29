from datetime import datetime, timedelta, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import current_user
from app.core.security import access_token, hash_password, one_time_token, refresh_token, token_hash, verify_password
from app.core.email import send_email
from app.core.audit import audit
from app.auth.models import SessionToken, OneTimeToken, LoginAttempt
from app.users.models import User, Role

router=APIRouter()

def issue(db,user,family_id=None):
    raw=refresh_token(); family_id=family_id or secrets.token_hex(32)
    db.add(SessionToken(user_id=user.id,refresh_token_hash=token_hash(raw),family_id=family_id,expires_at=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_expire_days)))
    db.commit()
    return {"access_token":access_token(user.id,user.role.value),"refresh_token":raw,"token_type":"bearer","role":user.role}

def create_one_time(db,user,purpose,hours=24):
    raw=one_time_token(); db.add(OneTimeToken(user_id=user.id,token_hash=token_hash(raw),purpose=purpose,expires_at=datetime.now(timezone.utc)+timedelta(hours=hours))); db.commit(); return raw

def attempt_row(db,email,ip):
    return db.scalar(select(LoginAttempt).where(LoginAttempt.email==email,LoginAttempt.ip_address==ip))

def failed_login(db,email,ip):
    now=datetime.now(timezone.utc); row=attempt_row(db,email,ip)
    if row is None:
        row=LoginAttempt(email=email,ip_address=ip,failed_count=0,last_attempt_at=now); db.add(row)
    row.failed_count+=1; row.last_attempt_at=now
    if row.failed_count>=settings.login_max_attempts: row.locked_until=now+timedelta(minutes=settings.login_lockout_minutes)
    db.commit()

@router.post("/register",status_code=201)
def register(email:str,full_name:str,password:str,db:Session=Depends(get_db)):
    email=email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already registered")
    try: user=User(email=email,full_name=full_name,password_hash=hash_password(password),role=Role.USER)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    db.add(user); db.commit(); db.refresh(user)
    token=create_one_time(db,user,"email_verification")
    try: send_email(email,"Verify your Money Maintainer email",f"Verify your email: {settings.app_base_url}/api/v1/auth/verify-email?token={token}")
    except RuntimeError:
        if settings.require_email_verification or settings.environment.lower() == "production":
            raise HTTPException(503,"Email service is not configured")
    audit(db,user.id,"REGISTER","User",str(user.id)); db.commit()
    return {**issue(db,user),"message":"Registration successful. Check your email to verify your account."}

@router.post("/login")
def login(email:str,password:str,request:Request,db:Session=Depends(get_db)):
    email=email.lower(); ip=request.client.host if request.client else "unknown"; row=attempt_row(db,email,ip); now=datetime.now(timezone.utc)
    if row and row.locked_until and row.locked_until>now: raise HTTPException(429,"Too many failed login attempts")
    user=db.scalar(select(User).where(User.email==email))
    if not user or not user.is_active or not verify_password(password,user.password_hash):
        failed_login(db,email,ip); raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid credentials")
    if settings.require_email_verification and not user.is_email_verified: raise HTTPException(403,"Email verification required")
    if row: row.failed_count=0; row.locked_until=None; db.commit()
    audit(db,user.id,"LOGIN","User",str(user.id)); db.commit(); return issue(db,user)

@router.post("/refresh")
def refresh(refresh_token_value:str,db:Session=Depends(get_db)):
    s=db.scalar(select(SessionToken).where(SessionToken.refresh_token_hash==token_hash(refresh_token_value))); now=datetime.now(timezone.utc)
    if not s or s.expires_at<=now: raise HTTPException(401,"Invalid refresh token")
    user=db.get(User,s.user_id)
    if not user or not user.is_active: raise HTTPException(401,"Inactive account")
    if s.revoked_at:
        db.execute(update(SessionToken).where(SessionToken.family_id==s.family_id).values(revoked_at=now)); db.commit(); raise HTTPException(401,"Refresh token reuse detected")
    s.revoked_at=now; db.commit(); return issue(db,user,s.family_id)

@router.post("/logout")
def logout(refresh_token_value:str,db:Session=Depends(get_db)):
    s=db.scalar(select(SessionToken).where(SessionToken.refresh_token_hash==token_hash(refresh_token_value)))
    if s: s.revoked_at=datetime.now(timezone.utc); audit(db,s.user_id,"LOGOUT","Session",str(s.id)); db.commit()
    return {"message":"Logged out"}

@router.post("/verify-email")
def verify_email(token:str,db:Session=Depends(get_db)):
    row=db.scalar(select(OneTimeToken).where(OneTimeToken.token_hash==token_hash(token),OneTimeToken.purpose=="email_verification")); now=datetime.now(timezone.utc)
    if not row or row.used_at or row.expires_at<=now: raise HTTPException(400,"Invalid or expired verification token")
    user=db.get(User,row.user_id); user.is_email_verified=True; row.used_at=now; audit(db,user.id,"EMAIL_VERIFIED","User",str(user.id)); db.commit(); return {"message":"Email verified"}

@router.post("/forgot-password")
def forgot_password(email:str,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==email.lower()))
    if user and user.is_active:
        token=create_one_time(db,user,"password_reset",hours=1)
        try: send_email(user.email,"Reset your Money Maintainer password",f"Reset your password: {settings.app_base_url}/reset-password?token={token}")
        except RuntimeError: pass
        audit(db,user.id,"PASSWORD_RESET_REQUEST","User",str(user.id)); db.commit()
    return {"message":"If the account exists, a reset email has been sent"}

@router.post("/reset-password")
def reset_password(token:str,password:str,db:Session=Depends(get_db)):
    row=db.scalar(select(OneTimeToken).where(OneTimeToken.token_hash==token_hash(token),OneTimeToken.purpose=="password_reset")); now=datetime.now(timezone.utc)
    if not row or row.used_at or row.expires_at<=now: raise HTTPException(400,"Invalid or expired reset token")
    try: hashed=hash_password(password)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    user=db.get(User,row.user_id); user.password_hash=hashed; row.used_at=now
    db.execute(update(SessionToken).where(SessionToken.user_id==user.id).values(revoked_at=now)); audit(db,user.id,"PASSWORD_RESET","User",str(user.id)); db.commit(); return {"message":"Password reset"}

@router.get("/me")
def me(user:User=Depends(current_user)):
    return {"id":user.id,"email":user.email,"full_name":user.full_name,"role":user.role,"is_email_verified":user.is_email_verified}

@router.post("/change-password")
def change_password(password:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    try: user.password_hash=hash_password(password)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    now=datetime.now(timezone.utc); db.execute(update(SessionToken).where(SessionToken.user_id==user.id).values(revoked_at=now)); audit(db,user.id,"PASSWORD_CHANGED","User",str(user.id)); db.commit(); return {"message":"Password changed"}
