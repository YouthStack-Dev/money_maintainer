from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_recurring_transactions"
down_revision = "0006_security_hardening"
branch_labels = None
depends_on = None

PERMISSIONS = [f"recurring_transactions.{action}" for action in ("read", "create", "update", "delete")]


def upgrade():
    recurring_frequency = postgresql.ENUM("WEEKLY", "MONTHLY", "YEARLY", name="recurring_frequency")
    recurring_frequency.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "recurring_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("transaction_type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("frequency", recurring_frequency, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true"), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("transaction_type IN ('INCOME','EXPENSE','REFUND')", name="ck_recurring_transaction_type"),
        sa.CheckConstraint("amount > 0", name="ck_recurring_transaction_amount_positive"),
        sa.CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_recurring_transaction_date_bounds"),
    )
    op.create_table(
        "recurring_transaction_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recurring_transaction_id", sa.Integer(), sa.ForeignKey("recurring_transactions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("scheduled_run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("transaction_id", sa.Integer(), sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("recurring_transaction_id", "scheduled_run_at", name="uq_recurring_run_schedule"),
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO permissions (code) VALUES "
            + ",".join(f"(:p{i})" for i in range(len(PERMISSIONS)))
            + " ON CONFLICT (code) DO NOTHING"
        ),
        {f"p{i}": permission for i, permission in enumerate(PERMISSIONS)},
    )
    rows = conn.execute(sa.text("SELECT id, code FROM permissions WHERE code LIKE 'recurring_transactions.%'")).mappings().all()
    for role in ("USER", "ADMIN", "SUPER_ADMIN"):
        for row in rows:
            conn.execute(
                sa.text("INSERT INTO role_permissions (role, permission_id) VALUES (:role, :permission_id) ON CONFLICT DO NOTHING"),
                {"role": role, "permission_id": row["id"]},
            )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE permission_id IN "
            "(SELECT id FROM permissions WHERE code LIKE 'recurring_transactions.%')"
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'recurring_transactions.%'"))
    op.drop_table("recurring_transaction_runs")
    op.drop_table("recurring_transactions")
    postgresql.ENUM("WEEKLY", "MONTHLY", "YEARLY", name="recurring_frequency").drop(op.get_bind(), checkfirst=True)
