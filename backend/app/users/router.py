from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import admin_user
from app.core.security import hash_password
from app.users.models import User,Role

router=APIRouter()

@router.get("")
def list_users(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    return db.scalars(select(User).where(User.role==Role.USER).order_by(User.id)).all()

@router.post("",status_code=201)
def create_user(email:str,full_name:str,password:str,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    email=email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already registered")
    user=User(email=email,full_name=full_name,password_hash=hash_password(password))
    db.add(user);db.commit();db.refresh(user);return user

@router.get("/{user_id}")
def get_user(user_id:int,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user or user.role!=Role.USER: raise HTTPException(404,"User not found")
    return user

@router.patch("/{user_id}")
def update_user(user_id:int,full_name:str|None=None,is_active:bool|None=None,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user or user.role!=Role.USER: raise HTTPException(404,"User not found")
    if full_name is not None:user.full_name=full_name
    if is_active is not None:user.is_active=is_active
    db.commit();db.refresh(user);return user

@router.delete("/{user_id}")
def delete_user(user_id:int,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user or user.role!=Role.USER: raise HTTPException(404,"User not found")
    user.is_active=False;db.commit();return {"message":"User deactivated"}
