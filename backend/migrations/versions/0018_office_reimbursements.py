from alembic import op
import sqlalchemy as sa

revision = "0018_office_reimbursements"
down_revision = "0017_wealth_dashboard_permissions"
branch_labels = None
depends_on = None

def upgrade():
    status = sa.Enum("PENDING", "REIMBURSED", "CANCELLED", name="office_reimbursement_status")
    status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "office_reimbursements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expense_transaction_id", sa.Integer(), sa.ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("reimbursement_transaction_id", sa.Integer(), sa.ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=True, unique=True),
        sa.Column("amount", sa.Numeric(15,2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", status, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_office_reimbursements_user_id", "office_reimbursements", ["user_id"])
    op.create_index("ix_office_reimbursements_status", "office_reimbursements", ["status"])

def downgrade():
    op.drop_index("ix_office_reimbursements_status", table_name="office_reimbursements")
    op.drop_index("ix_office_reimbursements_user_id", table_name="office_reimbursements")
    op.drop_table("office_reimbursements")
    sa.Enum(name="office_reimbursement_status").drop(op.get_bind(), checkfirst=True)
