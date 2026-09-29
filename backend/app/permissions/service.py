from sqlalchemy import select
from sqlalchemy.orm import Session
from app.permissions.models import Permission, RolePermission
from app.users.models import User

PERMISSIONS=[f"{resource}.{action}" for resource in ("users","admins","accounts","categories","transactions","summary","budgets") for action in ("read","create","update","delete")]

def has_permission(db: Session,user: User,code: str) -> bool:
    if user.role.value == "SUPER_ADMIN": return True
    return db.scalar(select(RolePermission.id).join(Permission).where(RolePermission.role==user.role.value,Permission.code==code)) is not None
