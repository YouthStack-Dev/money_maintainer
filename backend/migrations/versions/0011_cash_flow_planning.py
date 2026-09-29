from alembic import op
import sqlalchemy as sa

revision = "0011_cash_flow_planning"
down_revision = "0010_financial_goals"
branch_labels = None
depends_on = None


def upgrade():
    flow_type = sa.Enum("INCOME", "EXPENSE", name="cash_flow_type")
    flow_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "cash_flow_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("starting_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("end_date >= start_date", name="ck_cash_flow_plan_dates"),
    )
    op.create_index("ix_cash_flow_plans_user_id", "cash_flow_plans", ["user_id"])

    op.create_table(
        "cash_flow_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("cash_flow_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("flow_type", flow_type, nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("planned_date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT")),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("note", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_cash_flow_item_amount_positive"),
    )
    op.create_index("ix_cash_flow_items_plan_id", "cash_flow_items", ["plan_id"])
    op.create_index("ix_cash_flow_items_planned_date", "cash_flow_items", ["planned_date"])

    conn = op.get_bind()
    permissions = [f"cash_flow.{a}" for a in ("read", "create", "update", "delete")]
    conn.execute(sa.text("INSERT INTO permissions (code) VALUES " + ",".join(f"(:p{i})" for i in range(4)) + " ON CONFLICT (code) DO NOTHING"), {f"p{i}": p for i,p in enumerate(permissions)})
    rows = conn.execute(sa.text("SELECT id FROM permissions WHERE code LIKE 'cash_flow.%'")).mappings().all()
    for role in ("USER", "ADMIN", "SUPER_ADMIN"):
        for row in rows:
            conn.execute(sa.text("INSERT INTO role_permissions (role, permission_id) VALUES (:role, :pid) ON CONFLICT DO NOTHING"), {"role": role, "pid": row["id"]})


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code LIKE 'cash_flow.%')"))
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'cash_flow.%'"))
    op.drop_index("ix_cash_flow_items_planned_date", table_name="cash_flow_items")
    op.drop_index("ix_cash_flow_items_plan_id", table_name="cash_flow_items")
    op.drop_table("cash_flow_items")
    op.drop_index("ix_cash_flow_plans_user_id", table_name="cash_flow_plans")
    op.drop_table("cash_flow_plans")
    sa.Enum(name="cash_flow_type").drop(op.get_bind(), checkfirst=True)
