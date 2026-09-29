from alembic import op
import sqlalchemy as sa
revision="0001_auth_foundation";down_revision=None;branch_labels=None;depends_on=None

def upgrade():
    role=sa.Enum("USER","ADMIN","SUPER_ADMIN",name="user_role");role.create(op.get_bind(),checkfirst=True)
    op.create_table("users",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("email",sa.String(320),nullable=False,unique=True),
        sa.Column("full_name",sa.String(120),nullable=False),
        sa.Column("password_hash",sa.String(255),nullable=False),
        sa.Column("role",role,nullable=False,server_default="USER"),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("is_email_verified",sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("sessions",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("refresh_token_hash",sa.String(64),nullable=False,unique=True),
        sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("revoked_at",sa.DateTime(timezone=True)),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("one_time_tokens",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("token_hash",sa.String(64),nullable=False,unique=True),
        sa.Column("purpose",sa.String(40),nullable=False),
        sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("used_at",sa.DateTime(timezone=True)))

def downgrade():
    op.drop_table("one_time_tokens");op.drop_table("sessions");op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind(),checkfirst=True)
