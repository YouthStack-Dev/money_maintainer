from alembic import op
import sqlalchemy as sa

revision = "0015_net_worth_snapshots"
down_revision = "0014_assets"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "net_worth_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("liquid_assets", sa.Numeric(20, 2), nullable=False),
        sa.Column("investment_value", sa.Numeric(20, 2), nullable=False),
        sa.Column("other_assets", sa.Numeric(20, 2), nullable=False),
        sa.Column("lent_receivables", sa.Numeric(20, 2), nullable=False),
        sa.Column("credit_card_debt", sa.Numeric(20, 2), nullable=False),
        sa.Column("borrowed_debt", sa.Numeric(20, 2), nullable=False),
        sa.Column("total_assets", sa.Numeric(20, 2), nullable=False),
        sa.Column("total_liabilities", sa.Numeric(20, 2), nullable=False),
        sa.Column("net_worth", sa.Numeric(20, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "snapshot_date", name="uq_net_worth_snapshot_user_date"),
    )
    op.create_index("ix_net_worth_snapshots_user_id", "net_worth_snapshots", ["user_id"])
    op.create_index("ix_net_worth_snapshots_snapshot_date", "net_worth_snapshots", ["snapshot_date"])

    conn = op.get_bind()
    permissions = [f"net_worth.{a}" for a in ("read", "create", "update", "delete")]
    conn.execute(
        sa.text(
            "INSERT INTO permissions (code) VALUES "
            + ",".join(f"(:p{i})" for i in range(4))
            + " ON CONFLICT (code) DO NOTHING"
        ),
        {f"p{i}": permission for i, permission in enumerate(permissions)},
    )
    rows = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code LIKE 'net_worth.%'")
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
            "(SELECT id FROM permissions WHERE code LIKE 'net_worth.%')"
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'net_worth.%'"))
    op.drop_index("ix_net_worth_snapshots_snapshot_date", table_name="net_worth_snapshots")
    op.drop_index("ix_net_worth_snapshots_user_id", table_name="net_worth_snapshots")
    op.drop_table("net_worth_snapshots")
