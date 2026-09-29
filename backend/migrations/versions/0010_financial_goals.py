from alembic import op
import sqlalchemy as sa

revision = "0010_financial_goals"
down_revision = "0009_credit_card_control"
branch_labels = None
depends_on = None

PERMISSIONS = [f"goals.{action}" for action in ("read", "create", "update", "delete")]


def upgrade():
    goal_status = sa.Enum("ACTIVE", "COMPLETED", "CANCELLED", name="goal_status")
    goal_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "financial_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("target_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", goal_status, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("target_amount > 0", name="ck_financial_goals_target_positive"),
    )
    op.create_index("ix_financial_goals_user_id", "financial_goals", ["user_id"])

    op.create_table(
        "goal_contributions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("financial_goals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("contribution_date", sa.Date(), nullable=False),
        sa.Column("note", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_goal_contributions_amount_positive"),
    )
    op.create_index("ix_goal_contributions_goal_id", "goal_contributions", ["goal_id"])

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO permissions (code) VALUES "
            + ",".join(f"(:p{i})" for i in range(4))
            + " ON CONFLICT (code) DO NOTHING"
        ),
        {f"p{i}": permission for i, permission in enumerate(PERMISSIONS)},
    )
    rows = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code LIKE 'goals.%'")
    ).mappings().all()
    for role in ("USER", "ADMIN", "SUPER_ADMIN"):
        for row in rows:
            conn.execute(
                sa.text(
                    "INSERT INTO role_permissions (role, permission_id) "
                    "VALUES (:role, :pid) ON CONFLICT DO NOTHING"
                ),
                {"role": role, "pid": row["id"]},
            )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE permission_id IN "
            "(SELECT id FROM permissions WHERE code LIKE 'goals.%')"
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'goals.%'"))
    op.drop_index("ix_goal_contributions_goal_id", table_name="goal_contributions")
    op.drop_table("goal_contributions")
    op.drop_index("ix_financial_goals_user_id", table_name="financial_goals")
    op.drop_table("financial_goals")
    sa.Enum(name="goal_status").drop(op.get_bind(), checkfirst=True)
