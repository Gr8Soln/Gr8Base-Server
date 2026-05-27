"""
pgvector similarity search utilities.
Used by resume and job repositories for semantic matching.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


async def cosine_similarity_search(
    session: AsyncSession,
    table: str,
    embedding_column: str,
    query_embedding: list[float],
    user_id: str,
    limit: int = 5,
    id_column: str = "id",
) -> list[str]:
    """
    Returns a list of UUIDs (as strings) from `table` ordered by
    cosine similarity to query_embedding, filtered by user_id.
    """
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    stmt = text(f"""
        SELECT {id_column}::text
        FROM {table}
        WHERE user_id = :user_id
          AND {embedding_column} IS NOT NULL
        ORDER BY {embedding_column} <=> :embedding::vector
        LIMIT :limit
    """)

    result = await session.execute(
        stmt,
        {"user_id": user_id, "embedding": embedding_str, "limit": limit},
    )
    return [row[0] for row in result.fetchall()]
