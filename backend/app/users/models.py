from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Role(str, Enum):
    USER="USER"
    ADMIN="ADMIN"
    SUPER_ADMIN="SUPER_ADMIN"

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(320),unique=True,index=True)
    full_name: Mapped[str]=mapped_column(String(120))
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[Role]=mapped_column(SAEnum(Role,name="user_role"),default=Role.USER)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    is_email_verified: Mapped[bool]=mapped_column(Boolean,default=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))
