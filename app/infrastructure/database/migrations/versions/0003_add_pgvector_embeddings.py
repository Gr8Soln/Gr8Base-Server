"""Add pgvector extension and embedding columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-26

"""
from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIM = 1536  # text-embedding-3-small


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding column to resumes
    op.execute(
        f"ALTER TABLE resumes ADD COLUMN IF NOT EXISTS embedding vector({EMBEDDING_DIM})"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_resumes_embedding "
        "ON resumes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    # Add embedding column to jobs
    op.execute(
        f"ALTER TABLE jobs ADD COLUMN IF NOT EXISTS embedding vector({EMBEDDING_DIM})"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_embedding "
        "ON jobs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_jobs_embedding")
    op.execute("DROP INDEX IF EXISTS ix_resumes_embedding")
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE resumes DROP COLUMN IF EXISTS embedding")
