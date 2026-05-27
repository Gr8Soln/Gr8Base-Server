"""Add jobs table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("raw_text", sa.Text, nullable=False, server_default=""),
        sa.Column("title", sa.String(500), nullable=False, server_default=""),
        sa.Column("company", sa.String(500), nullable=False, server_default=""),
        sa.Column("company_url", sa.String(1000), nullable=False, server_default=""),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("work_type", sa.String(50), nullable=False, server_default=""),
        sa.Column("role", sa.String(255), nullable=False, server_default=""),
        sa.Column("seniority", sa.String(100), nullable=False, server_default=""),
        sa.Column("domain", sa.String(255), nullable=False, server_default=""),
        sa.Column("required_skills", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("preferred_skills", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("soft_skills", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column(
            "tools_and_technologies", postgresql.JSON, nullable=False, server_default="[]"
        ),
        sa.Column("ats_keywords", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("hidden_signals", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("salary_min", sa.Integer, nullable=True),
        sa.Column("salary_max", sa.Integer, nullable=True),
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
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])


def downgrade() -> None:
    op.drop_table("jobs")
