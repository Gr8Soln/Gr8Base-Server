"""Career Profile Engine — Phase 1 Foundation

Creates all canonical career profile tables and extends the existing
career_profiles table with new fields.

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Extend existing career_profiles table ───────────────────────────────
    op.execute(
        "ALTER TABLE career_profiles ADD COLUMN IF NOT EXISTS address "
        "VARCHAR(500) NOT NULL DEFAULT ''"
    )
    op.execute(
        "ALTER TABLE career_profiles ADD COLUMN IF NOT EXISTS website "
        "VARCHAR(500) NOT NULL DEFAULT ''"
    )
    op.execute(
        "ALTER TABLE career_profiles ADD COLUMN IF NOT EXISTS summary_embedding "
        "VECTOR(1536)"
    )

    # ── Career Experiences ──────────────────────────────────────────────────
    op.create_table(
        "career_experiences",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company", sa.String(500), nullable=False),
        sa.Column("role", sa.String(500), nullable=False),
        sa.Column("start_date", sa.String(50), nullable=False),
        sa.Column("end_date", sa.String(50), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("employment_type", sa.String(50), nullable=False, server_default="full_time"),
        sa.Column("industry", sa.String(255), nullable=False, server_default=""),
        sa.Column("company_website", sa.String(500), nullable=False, server_default=""),
        sa.Column("responsibilities", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("achievements", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("technologies", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("impact_statements", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("related_projects", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("ai_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", sa.NullType(), nullable=True),
        sa.Column("enrichment_data", sa.JSON(), nullable=False, server_default="{}"),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_experiences_user_id", "career_experiences", ["user_id"])
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_career_experiences_embedding "
        "ON career_experiences USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )

    # ── Career Projects ─────────────────────────────────────────────────────
    op.create_table(
        "career_projects",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("role", sa.String(255), nullable=False, server_default=""),
        sa.Column("technologies", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("responsibilities", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("repository", sa.String(1000), nullable=False, server_default=""),
        sa.Column("demo_url", sa.String(1000), nullable=False, server_default=""),
        sa.Column("url", sa.String(1000), nullable=False, server_default=""),
        sa.Column("duration", sa.String(100), nullable=False, server_default=""),
        sa.Column("impact", sa.Text(), nullable=False, server_default=""),
        sa.Column("ai_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", sa.NullType(), nullable=True),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_projects_user_id", "career_projects", ["user_id"])
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_career_projects_embedding "
        "ON career_projects USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )

    # ── Career Skills ───────────────────────────────────────────────────────
    op.create_table(
        "career_skills",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="technical"),
        sa.Column("proficiency", sa.String(50), nullable=False, server_default=""),
        sa.Column("years_of_experience", sa.Float(), nullable=False, server_default="0.0"),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_skills_user_id", "career_skills", ["user_id"])

    # ── Career Technologies ─────────────────────────────────────────────────
    op.create_table(
        "career_technologies",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="tool"),
        sa.Column("proficiency", sa.String(50), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_technologies_user_id", "career_technologies", ["user_id"])

    # ── Career Education ────────────────────────────────────────────────────
    op.create_table(
        "career_education",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("institution", sa.String(500), nullable=False),
        sa.Column("degree", sa.String(500), nullable=False),
        sa.Column("field_of_study", sa.String(255), nullable=False, server_default=""),
        sa.Column("start_year", sa.Integer(), nullable=True),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("gpa", sa.Float(), nullable=True),
        sa.Column("honors", sa.String(500), nullable=False, server_default=""),
        sa.Column("activities", sa.Text(), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_education_user_id", "career_education", ["user_id"])

    # ── Career Certifications ───────────────────────────────────────────────
    op.create_table(
        "career_certifications",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("issuer", sa.String(500), nullable=False),
        sa.Column("issue_date", sa.String(50), nullable=False, server_default=""),
        sa.Column("expiry_date", sa.String(50), nullable=False, server_default=""),
        sa.Column("credential_url", sa.String(1000), nullable=False, server_default=""),
        sa.Column("credential_id", sa.String(255), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_certifications_user_id", "career_certifications", ["user_id"])

    # ── Career Awards ───────────────────────────────────────────────────────
    op.create_table(
        "career_awards",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("issuer", sa.String(500), nullable=False),
        sa.Column("date", sa.String(50), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_awards_user_id", "career_awards", ["user_id"])

    # ── Career Publications ─────────────────────────────────────────────────
    op.create_table(
        "career_publications",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("publisher", sa.String(500), nullable=False),
        sa.Column("date", sa.String(50), nullable=False, server_default=""),
        sa.Column("url", sa.String(1000), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_publications_user_id", "career_publications", ["user_id"])

    # ── Career Blogs ────────────────────────────────────────────────────────
    op.create_table(
        "career_blogs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("platform", sa.String(255), nullable=False, server_default=""),
        sa.Column("date", sa.String(50), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_blogs_user_id", "career_blogs", ["user_id"])

    # ── Career Languages ────────────────────────────────────────────────────
    op.create_table(
        "career_languages",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("proficiency", sa.String(50), nullable=False, server_default=""),
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
            nullable=False,
        ),
    )
    op.create_index("ix_career_languages_user_id", "career_languages", ["user_id"])

    # ── Ingestion Workflows ─────────────────────────────────────────────────
    op.create_table(
        "ingestion_workflows",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("source_file_key", sa.String(1000), nullable=False, server_default=""),
        sa.Column("source_file_name", sa.String(500), nullable=False, server_default=""),
        sa.Column("source_file_url", sa.String(1000), nullable=False, server_default=""),
        sa.Column("error_message", sa.Text(), nullable=False, server_default=""),
        sa.Column("events", sa.JSON(), nullable=False, server_default="[]"),
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
            nullable=False,
        ),
    )
    op.create_index("ix_ingestion_workflows_user_id", "ingestion_workflows", ["user_id"])


def downgrade() -> None:
    # ── Remove new columns from career_profiles ─────────────────────────────
    op.execute("ALTER TABLE career_profiles DROP COLUMN IF EXISTS summary_embedding")
    op.execute("ALTER TABLE career_profiles DROP COLUMN IF EXISTS website")
    op.execute("ALTER TABLE career_profiles DROP COLUMN IF EXISTS address")

    # ── Drop all new tables ─────────────────────────────────────────────────
    op.drop_table("ingestion_workflows")
    op.drop_table("career_languages")
    op.drop_table("career_blogs")
    op.drop_table("career_publications")
    op.drop_table("career_awards")
    op.drop_table("career_certifications")
    op.drop_table("career_education")
    op.drop_table("career_technologies")
    op.drop_table("career_skills")
    op.drop_table("career_projects")
    op.drop_table("career_experiences")
