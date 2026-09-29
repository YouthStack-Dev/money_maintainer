from alembic import op
import sqlalchemy as sa

revision="0012_financial_alerts"
down_revision="0011_cash_flow_planning"
branch_labels=None
depends_on=None

def upgrade():
    typ=sa.Enum("CREDIT_CARD_DUE","CREDIT_CARD_OVER_LIMIT","DEBT_DUE","DEBT_OVERDUE","GOAL_DEADLINE","CASH_FLOW_LOW",name="financial_alert_type")
    sev=sa.Enum("INFO","WARNING","CRITICAL",name="financial_alert_severity")
    typ.create(op.get_bind(),checkfirst=True); sev.create(op.get_bind(),checkfirst=True)
    op.create_table("financial_alerts",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("alert_type",typ,nullable=False),
        sa.Column("severity",sev,nullable=False),
        sa.Column("title",sa.String(160),nullable=False),
        sa.Column("message",sa.Text(),nullable=False),
        sa.Column("reference_id",sa.Integer(),nullable=True),
        sa.Column("is_read",sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_financial_alerts_user_id","financial_alerts",["user_id"])
    op.create_index("ix_financial_alerts_alert_type","financial_alerts",["alert_type"])
    op.create_index("ix_financial_alerts_created_at","financial_alerts",["created_at"])
    conn=op.get_bind()
    permissions=[f"alerts.{a}" for a in ("read","create","update","delete")]
    conn.execute(sa.text("INSERT INTO permissions (code) VALUES "+",".join(f"(:p{i})" for i in range(4))+" ON CONFLICT (code) DO NOTHING"),{f"p{i}":p for i,p in enumerate(permissions)})
    rows=conn.execute(sa.text("SELECT id FROM permissions WHERE code LIKE 'alerts.%'")).mappings().all()
    for role in ("USER","ADMIN","SUPER_ADMIN"):
        for row in rows: conn.execute(sa.text("INSERT INTO role_permissions (role,permission_id) VALUES (:role,:pid) ON CONFLICT DO NOTHING"),{"role":role,"pid":row["id"]})

def downgrade():
    conn=op.get_bind()
    conn.execute(sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code LIKE 'alerts.%')"))
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'alerts.%'"))
    op.drop_index("ix_financial_alerts_created_at",table_name="financial_alerts")
    op.drop_index("ix_financial_alerts_alert_type",table_name="financial_alerts")
    op.drop_index("ix_financial_alerts_user_id",table_name="financial_alerts")
    op.drop_table("financial_alerts")
    sa.Enum(name="financial_alert_severity").drop(op.get_bind(),checkfirst=True)
    sa.Enum(name="financial_alert_type").drop(op.get_bind(),checkfirst=True)
