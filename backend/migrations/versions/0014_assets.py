from alembic import op
import sqlalchemy as sa

revision = "0014_assets"
down_revision = "0013_investment_holdings"
branch_labels = None
depends_on = None


def upgrade():
    asset_type = sa.Enum(
        "PROPERTY", "VEHICLE", "GOLD", "OTHER", name="asset_type"
    )
    asset_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("asset_type", asset_type, nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("purchase_value", sa.Numeric(20, 2), nullable=False),
        sa.Column("current_value", sa.Numeric(20, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_assets_user_id", "assets", ["user_id"])
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"])

    conn = op.get_bind()
    permissions = [f"assets.{a}" for a in ("read", "create", "update", "delete")]
    conn.execute(
        sa.text(
            "INSERT INTO permissions (code) VALUES "
            + ",".join(f"(:p{i})" for i in range(4))
            + " ON CONFLICT (code) DO NOTHING"
        ),
        {f"p{i}": permission for i, permission in enumerate(permissions)},
    )
    rows = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code LIKE 'assets.%'")
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
            "(SELECT id FROM permissions WHERE code LIKE 'assets.%')"
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'assets.%'"))
    op.drop_index("ix_assets_asset_type", table_name="assets")
    op.drop_index("ix_assets_user_id", table_name="assets")
    op.drop_table("assets")
    sa.Enum(name="asset_type").drop(op.get_bind(), checkfirst=True)
