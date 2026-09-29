from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_categories"
down_revision = "0002_accounts"
branch_labels = None
depends_on = None


def upgrade():
    category_type = postgresql.ENUM("INCOME", "EXPENSE", name="category_type", create_type=False)
    category_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category_type", category_type, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])
    op.create_index("ix_categories_parent_id", "categories", ["parent_id"])


def downgrade():
    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_index("ix_categories_user_id", table_name="categories")
    op.drop_table("categories")
    sa.Enum(name="category_type").drop(op.get_bind(), checkfirst=True)
