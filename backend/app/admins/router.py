from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import admin_user,super_admin
from app.core.security import hash_password
from app.core.audit import audit
from app.users.models import User,Role

router=APIRouter()

@router.get("")
def list_admins(_:User=Depends(admin_user),db:Session=Depends(get_db)):
    return db.scalars(select(User).where(User.role.in_([Role.ADMIN,Role.SUPER_ADMIN])).order_by(User.id)).all()

@router.post("",status_code=201)
def create_admin(email:str,full_name:str,password:str,actor:User=Depends(super_admin),db:Session=Depends(get_db)):
    email=email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already registered")
    admin=User(email=email,full_name=full_name,password_hash=hash_password(password),role=Role.ADMIN)
    db.add(admin);db.commit();db.refresh(admin);audit(db,actor.id,"ADMIN_CREATED","User",str(admin.id));db.commit();return admin

@router.get("/{admin_id}")
def get_admin(admin_id:int,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    admin=db.get(User,admin_id)
    if not admin or admin.role not in {Role.ADMIN,Role.SUPER_ADMIN}: raise HTTPException(404,"Admin not found")
    return admin

@router.patch("/{admin_id}")
def update_admin(admin_id:int,full_name:str|None=None,is_active:bool|None=None,_:User=Depends(super_admin),db:Session=Depends(get_db)):
    admin=db.get(User,admin_id)
    if not admin or admin.role not in {Role.ADMIN,Role.SUPER_ADMIN}: raise HTTPException(404,"Admin not found")
    if full_name is not None:admin.full_name=full_name
    if is_active is not None:admin.is_active=is_active
    db.commit();db.refresh(admin);return admin

@router.delete("/{admin_id}")
def delete_admin(admin_id:int,_:User=Depends(super_admin),db:Session=Depends(get_db)):
    admin=db.get(User,admin_id)
    if not admin or admin.role not in {Role.ADMIN,Role.SUPER_ADMIN}: raise HTTPException(404,"Admin not found")
    admin.is_active=False;db.commit();return {"message":"Admin deactivated"}
