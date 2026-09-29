from alembic import op
import sqlalchemy as sa

revision = "0009_credit_card_control"
down_revision = "0008_debts_lending"
branch_labels = None
depends_on = None

PERMISSIONS = [f"credit_cards.{action}" for action in ("read", "create", "update", "delete")]


def upgrade():
    op.add_column("accounts", sa.Column("credit_limit", sa.Numeric(15, 2), nullable=True))
    op.add_column("accounts", sa.Column("statement_day", sa.Integer(), nullable=True))
    op.add_column("accounts", sa.Column("payment_due_day", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_accounts_credit_limit_positive",
        "accounts",
        "credit_limit IS NULL OR credit_limit > 0",
    )
    op.create_check_constraint(
        "ck_accounts_statement_day_valid",
        "accounts",
        "statement_day IS NULL OR statement_day BETWEEN 1 AND 31",
    )
    op.create_check_constraint(
        "ck_accounts_payment_due_day_valid",
        "accounts",
        "payment_due_day IS NULL OR payment_due_day BETWEEN 1 AND 31",
    )

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
        sa.text("SELECT id FROM permissions WHERE code LIKE 'credit_cards.%'")
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
            "(SELECT id FROM permissions WHERE code LIKE 'credit_cards.%')"
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code LIKE 'credit_cards.%'"))
    op.drop_constraint("ck_accounts_payment_due_day_valid", "accounts", type_="check")
    op.drop_constraint("ck_accounts_statement_day_valid", "accounts", type_="check")
    op.drop_constraint("ck_accounts_credit_limit_positive", "accounts", type_="check")
    op.drop_column("accounts", "payment_due_day")
    op.drop_column("accounts", "statement_day")
    op.drop_column("accounts", "credit_limit")
