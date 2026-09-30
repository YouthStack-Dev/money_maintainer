from alembic import op
import sqlalchemy as sa

revision = "0019_office_reimbursement_permissions"
down_revision = "0018_office_reimbursements"
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    permissions = [f"office_reimbursements.{a}" for a in ("read", "create", "update", "delete")]
    conn.execute(
        sa.text("INSERT INTO permissions (code) VALUES " + ",".join(f"(:p{i})" for i in range(4)) + " ON CONFLICT (code) DO NOTHING"),
        {f"p{i}": permission for i, permission in enumerate(permissions)},
    )
    rows = conn.execute(sa.text("SELECT id FROM permissions WHERE code LIKE 'office_reimbursements.%'")).mappings().all()
    for role in ("USER", "ADMIN", "SUPER_ADMIN"):
        for row in rows:
            conn.execute(sa.text("INSERT INTO role_permissions (role,permission_id) VALUES (:role,:pid) ON CONFLICT DO NOTHING"), {"role": role, "pid": row["id"]})

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code LIKE 'office_reimbursements.%')"))
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'office_reimbursements.%'"))
