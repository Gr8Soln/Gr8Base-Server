"""Add resumes table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_url", sa.String(1000), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False, server_default=""),
        sa.Column("skills", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("experience", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("projects", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("education", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("certifications", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("languages", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("label", sa.String(255), nullable=False, server_default=""),
        sa.Column("strategy", sa.String(100), nullable=True),
        sa.Column(
            "parent_resume_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resumes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("ats_score_snapshot", sa.Float, nullable=True),
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
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_index("ix_resumes_parent_resume_id", "resumes", ["parent_resume_id"])


def downgrade() -> None:
    op.drop_table("resumes")
