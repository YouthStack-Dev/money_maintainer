from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import admin_user
from app.core.security import hash_password
from app.users.models import User,Role

router=APIRouter()

def public_user(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

@router.get("")
def list_users(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    users=db.scalars(select(User).where(User.role==Role.USER).order_by(User.id)).all()
    return [public_user(user) for user in users]

@router.post("",status_code=201)
def create_user(email:str,full_name:str,password:str,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    email=email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already registered")
    if not full_name.strip(): raise HTTPException(422,"Full name is required")
    try: hashed=hash_password(password)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    user=User(email=email,full_name=full_name.strip(),password_hash=hashed)
    db.add(user);db.commit();db.refresh(user);return public_user(user)

@router.get("/{user_id}")
def get_user(user_id:int,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user or user.role!=Role.USER: raise HTTPException(404,"User not found")
    return public_user(user)

@router.patch("/{user_id}")
def update_user(user_id:int,full_name:str|None=None,is_active:bool|None=None,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user or user.role!=Role.USER: raise HTTPException(404,"User not found")
    if full_name is not None:
        if not full_name.strip(): raise HTTPException(422,"Full name is required")
        user.full_name=full_name.strip()
    if is_active is not None:user.is_active=is_active
    db.commit();db.refresh(user);return public_user(user)

@router.delete("/{user_id}")
def delete_user(user_id:int,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user or user.role!=Role.USER: raise HTTPException(404,"User not found")
    user.is_active=False;db.commit();return {"message":"User deactivated"}
