"""Initial users and career profiles tables

Revision ID: 0001
Revises:
Create Date: 2026-05-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_superuser", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "career_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("headline", sa.String(500), nullable=False, server_default=""),
        sa.Column("summary", sa.Text, nullable=False, server_default=""),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("phone", sa.String(50), nullable=False, server_default=""),
        sa.Column("linkedin_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("github_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("portfolio_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("years_of_experience", sa.Integer, nullable=False, server_default="0"),
        sa.Column("target_roles", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("target_industries", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("target_salary_min", sa.Integer, nullable=True),
        sa.Column("target_salary_max", sa.Integer, nullable=True),
        sa.Column("preferred_work_type", sa.String(50), nullable=False, server_default=""),
        sa.Column("writing_tone", sa.String(100), nullable=False, server_default="professional"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_career_profiles_user_id", "career_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("career_profiles")
    op.drop_table("users")
