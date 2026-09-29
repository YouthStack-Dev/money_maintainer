from alembic import op
import sqlalchemy as sa

revision = "0016_investment_transactions"
down_revision = "0015_net_worth_snapshots"
branch_labels = None
depends_on = None


def upgrade():
    tx_type = sa.Enum("BUY", "SELL", name="investment_transaction_type")
    tx_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "investment_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("holding_id", sa.Integer(), sa.ForeignKey("investment_holdings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("transaction_type", tx_type, nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("price", sa.Numeric(20, 8), nullable=False),
        sa.Column("fees", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("transaction_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_investment_transactions_user_id", "investment_transactions", ["user_id"])
    op.create_index("ix_investment_transactions_holding_id", "investment_transactions", ["holding_id"])
    op.create_index("ix_investment_transactions_transaction_date", "investment_transactions", ["transaction_date"])

    conn = op.get_bind()
    permissions = [f"investment_transactions.{a}" for a in ("read", "create", "update", "delete")]
    conn.execute(
        sa.text(
            "INSERT INTO permissions (code) VALUES "
            + ",".join(f"(:p{i})" for i in range(4))
            + " ON CONFLICT (code) DO NOTHING"
        ),
        {f"p{i}": permission for i, permission in enumerate(permissions)},
    )
    rows = conn.execute(sa.text("SELECT id FROM permissions WHERE code LIKE 'investment_transactions.%'")).mappings().all()
    for role in ("USER", "ADMIN", "SUPER_ADMIN"):
        for row in rows:
            conn.execute(
                sa.text(
                    "INSERT INTO role_permissions (role,permission_id) VALUES (:role,:pid) ON CONFLICT DO NOTHING"
                ),
                {"role": role, "pid": row["id"]},
            )


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text(
        "DELETE FROM role_permissions WHERE permission_id IN "
        "(SELECT id FROM permissions WHERE code LIKE 'investment_transactions.%')"
    ))
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'investment_transactions.%'"))
    op.drop_index("ix_investment_transactions_transaction_date", table_name="investment_transactions")
    op.drop_index("ix_investment_transactions_holding_id", table_name="investment_transactions")
    op.drop_index("ix_investment_transactions_user_id", table_name="investment_transactions")
    op.drop_table("investment_transactions")
    sa.Enum(name="investment_transaction_type").drop(op.get_bind(), checkfirst=True)
