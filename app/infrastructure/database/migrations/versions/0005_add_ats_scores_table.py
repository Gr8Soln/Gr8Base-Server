"""Add ats_scores table

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-26
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ats_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("overall_score", sa.Float, nullable=False),
        sa.Column("dimensions", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("dimension_breakdown", postgresql.JSON, nullable=False, server_default="{}"),
        sa.Column("missing_keywords", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("weak_sections", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("recommendations", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("recruiter_critique", sa.Text, nullable=False, server_default=""),
        sa.Column("is_ats_safe", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("safety_issues", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_ats_scores_user_id", "ats_scores", ["user_id"])
    op.create_index("ix_ats_scores_resume_id", "ats_scores", ["resume_id"])
    op.create_index("ix_ats_scores_job_id", "ats_scores", ["job_id"])


def downgrade() -> None:
    op.drop_table("ats_scores")
