from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class SessionToken(Base):
    __tablename__="sessions"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    refresh_token_hash: Mapped[str]=mapped_column(String(64),unique=True,index=True)
    family_id: Mapped[str]=mapped_column(String(64),index=True)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class LoginAttempt(Base):
    __tablename__="login_attempts"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(320),index=True)
    ip_address: Mapped[str]=mapped_column(String(64),index=True)
    failed_count: Mapped[int]=mapped_column(default=0,nullable=False)
    locked_until: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    last_attempt_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class OneTimeToken(Base):
    __tablename__="one_time_tokens"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    token_hash: Mapped[str]=mapped_column(String(64),unique=True,index=True)
    purpose: Mapped[str]=mapped_column(String(40),index=True)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
