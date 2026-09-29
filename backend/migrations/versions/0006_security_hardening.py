from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision="0006_security_hardening"
down_revision="0005_budgets"
branch_labels=None
depends_on=None

PERMISSIONS=[f"{r}.{a}" for r in ("users","admins","accounts","categories","transactions","summary","budgets") for a in ("read","create","update","delete")]

def upgrade():
    op.add_column("sessions",sa.Column("family_id",sa.String(64),nullable=True))
    op.execute(sa.text("UPDATE sessions SET family_id = md5(refresh_token_hash) WHERE family_id IS NULL"))
    op.alter_column("sessions","family_id",nullable=False)
    op.create_index("ix_sessions_family_id","sessions",["family_id"])
    op.create_table("permissions",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("code",sa.String(100),unique=True,index=True,nullable=False))
    op.create_table("role_permissions",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("role",sa.String(30),index=True,nullable=False),sa.Column("permission_id",sa.Integer(),sa.ForeignKey("permissions.id",ondelete="CASCADE"),index=True,nullable=False),sa.UniqueConstraint("role","permission_id"))
    op.create_table("audit_logs",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("actor_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),index=True),sa.Column("action",sa.String(80),index=True,nullable=False),sa.Column("target_type",sa.String(80)),sa.Column("target_id",sa.String(80)),sa.Column("metadata_json",postgresql.JSONB(),nullable=False,server_default=sa.text("'{}'::jsonb")),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("login_attempts",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("email",sa.String(320),index=True,nullable=False),sa.Column("ip_address",sa.String(64),index=True,nullable=False),sa.Column("failed_count",sa.Integer(),nullable=False,server_default="0"),sa.Column("locked_until",sa.DateTime(timezone=True)),sa.Column("last_attempt_at",sa.DateTime(timezone=True),nullable=False))
    conn=op.get_bind(); conn.execute(sa.text("INSERT INTO permissions (code) VALUES "+",".join("(:p%d)"%i for i in range(len(PERMISSIONS)))),{f"p{i}":p for i,p in enumerate(PERMISSIONS)})
    rows=conn.execute(sa.text("SELECT id, code FROM permissions")).mappings().all()
    for role in ("USER","ADMIN","SUPER_ADMIN"):
        for row in rows:
            if role=="USER" and not row["code"].startswith(("accounts.","categories.","transactions.","summary.","budgets.")): continue
            conn.execute(sa.text("INSERT INTO role_permissions (role,permission_id) VALUES (:r,:p) ON CONFLICT DO NOTHING"),{"r":role,"p":row["id"]})

def downgrade():
    op.drop_table("login_attempts"); op.drop_table("audit_logs"); op.drop_table("role_permissions"); op.drop_table("permissions")
    op.drop_index("ix_sessions_family_id",table_name="sessions")
    op.drop_column("sessions","family_id")
