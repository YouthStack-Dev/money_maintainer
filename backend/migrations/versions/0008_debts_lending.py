from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0008_debts_lending"
down_revision="0007_recurring_transactions"
branch_labels=None
depends_on=None
PERMISSIONS=[f"debts.{a}" for a in ("read","create","update","delete")]

def upgrade():
    direction=postgresql.ENUM("BORROWED","LENT",name="debt_direction"); direction.create(op.get_bind(),checkfirst=True)
    status=postgresql.ENUM("ACTIVE","PARTIALLY_PAID","SETTLED","CANCELLED",name="debt_status"); status.create(op.get_bind(),checkfirst=True)
    op.create_table("debts",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True),
        sa.Column("direction",direction,nullable=False,index=True),
        sa.Column("account_id",sa.Integer(),sa.ForeignKey("accounts.id",ondelete="RESTRICT"),nullable=False,index=True),
        sa.Column("person_name",sa.String(120),nullable=False),
        sa.Column("description",sa.Text()),
        sa.Column("original_amount",sa.Numeric(15,2),nullable=False),
        sa.Column("outstanding_amount",sa.Numeric(15,2),nullable=False),
        sa.Column("due_date",sa.Date()),
        sa.Column("status",status,nullable=False,server_default="ACTIVE",index=True),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("original_amount > 0",name="ck_debt_original_positive"),
        sa.CheckConstraint("outstanding_amount >= 0",name="ck_debt_outstanding_nonnegative"),
        sa.CheckConstraint("outstanding_amount <= original_amount",name="ck_debt_outstanding_lte_original"))
    op.create_table("debt_repayments",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("debt_id",sa.Integer(),sa.ForeignKey("debts.id",ondelete="CASCADE"),nullable=False,index=True),
        sa.Column("account_id",sa.Integer(),sa.ForeignKey("accounts.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("transaction_id",sa.Integer(),sa.ForeignKey("transactions.id",ondelete="RESTRICT"),nullable=False,unique=True),
        sa.Column("amount",sa.Numeric(15,2),nullable=False),
        sa.Column("repayment_date",sa.Date(),nullable=False),
        sa.Column("note",sa.Text()),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("amount > 0",name="ck_debt_repayment_positive"),
        sa.UniqueConstraint("debt_id","transaction_id",name="uq_debt_repayment_transaction"))
    conn=op.get_bind()
    conn.execute(sa.text("INSERT INTO permissions (code) VALUES "+",".join(f"(:p{i})" for i in range(4))+" ON CONFLICT (code) DO NOTHING"),{f"p{i}":p for i,p in enumerate(PERMISSIONS)})
    rows=conn.execute(sa.text("SELECT id FROM permissions WHERE code LIKE 'debts.%'")).mappings().all()
    for role in ("USER","ADMIN","SUPER_ADMIN"):
        for row in rows: conn.execute(sa.text("INSERT INTO role_permissions (role,permission_id) VALUES (:role,:pid) ON CONFLICT DO NOTHING"),{"role":role,"pid":row["id"]})

def downgrade():
    conn=op.get_bind()
    conn.execute(sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code LIKE 'debts.%')"))
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'debts.%'"))
    op.drop_table("debt_repayments"); op.drop_table("debts")
    postgresql.ENUM("BORROWED","LENT",name="debt_direction").drop(op.get_bind(),checkfirst=True)
    postgresql.ENUM("ACTIVE","PARTIALLY_PAID","SETTLED","CANCELLED",name="debt_status").drop(op.get_bind(),checkfirst=True)
