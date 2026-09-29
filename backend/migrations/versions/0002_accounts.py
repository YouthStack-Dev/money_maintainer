from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_accounts"
down_revision = "0001_auth_foundation"
branch_labels = None
depends_on = None


def upgrade():
    account_type = postgresql.ENUM(
        "CASH", "BANK_ACCOUNT", "CREDIT_CARD", "WALLET", name="account_type", create_type=False
    )
    account_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("account_type", account_type, nullable=False),
        sa.Column("institution_name", sa.String(120)),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("opening_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])


def downgrade():
    op.drop_index("ix_accounts_user_id", table_name="accounts")
    op.drop_table("accounts")
    sa.Enum(name="account_type").drop(op.get_bind(), checkfirst=True)
