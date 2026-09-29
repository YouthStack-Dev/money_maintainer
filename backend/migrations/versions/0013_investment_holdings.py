from alembic import op
import sqlalchemy as sa

revision = "0013_investment_holdings"
down_revision = "0012_financial_alerts"
branch_labels = None
depends_on = None


def upgrade():
    investment_type = sa.Enum(
        "STOCK", "MUTUAL_FUND", "ETF", "BOND", "CRYPTO", "OTHER",
        name="investment_type",
    )
    investment_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "investment_holdings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("investment_type", investment_type, nullable=False),
        sa.Column("symbol", sa.String(40), nullable=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("average_cost", sa.Numeric(20, 8), nullable=False),
        sa.Column("current_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_investment_holdings_user_id", "investment_holdings", ["user_id"])
    op.create_index("ix_investment_holdings_investment_type", "investment_holdings", ["investment_type"])
    op.create_index("ix_investment_holdings_symbol", "investment_holdings", ["symbol"])

    conn = op.get_bind()
    permissions = [f"investments.{a}" for a in ("read", "create", "update", "delete")]
    conn.execute(
        sa.text(
            "INSERT INTO permissions (code) VALUES "
            + ",".join(f"(:p{i})" for i in range(4))
            + " ON CONFLICT (code) DO NOTHING"
        ),
        {f"p{i}": permission for i, permission in enumerate(permissions)},
    )
    rows = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code LIKE 'investments.%'")
    ).mappings().all()
    for role in ("USER", "ADMIN", "SUPER_ADMIN"):
        for row in rows:
            conn.execute(
                sa.text(
                    "INSERT INTO role_permissions (role,permission_id) "
                    "VALUES (:role,:pid) ON CONFLICT DO NOTHING"
                ),
                {"role": role, "pid": row["id"]},
            )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE permission_id IN "
            "(SELECT id FROM permissions WHERE code LIKE 'investments.%')"
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'investments.%'"))
    op.drop_index("ix_investment_holdings_symbol", table_name="investment_holdings")
    op.drop_index("ix_investment_holdings_investment_type", table_name="investment_holdings")
    op.drop_index("ix_investment_holdings_user_id", table_name="investment_holdings")
    op.drop_table("investment_holdings")
    sa.Enum(name="investment_type").drop(op.get_bind(), checkfirst=True)
