from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.audit.models import AuditLog


def audit(db: Session, actor_id: int | None, action: str, target_type: str | None = None,
          target_id: str | None = None, metadata: dict | None = None) -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, target_type=target_type,
                    target_id=target_id, metadata_json=metadata or {},
                    created_at=datetime.now(timezone.utc)))
