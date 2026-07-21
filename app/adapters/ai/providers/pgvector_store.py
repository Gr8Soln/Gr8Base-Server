import uuid

from app.application.ports.ai.vector_store_port import VectorStorePort
from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.vector.pgvector_client import (
    cosine_similarity_search as _pg_cosine_search,
)

logger = get_logger(__name__)


class PgVectorStore(VectorStorePort):
    """pgvector-based vector store adapter.

    Wraps existing pgvector_client.py and provides the port interface.
    For future providers (Pinecone, Qdrant, etc.), implement the same port.
    """

    async def store_embedding(
        self,
        entity_id: uuid.UUID,
        embedding: list[float],
        entity_type: str,
        metadata: dict | None = None,
    ) -> None:
        """Store an embedding. Currently handled by SQLAlchemy models directly
        via the repository layer. This adapter delegates to the DB model."""
        # Embeddings are stored via SQLAlchemy models in the repository layer.
        # The pgvector column is part of the entity model (e.g., ExperienceModel.embedding).
        # This method exists for the port interface but actual storage is handled
        # by the repository's update method setting the embedding column.
        logger.info(
            "pgvector_store_embedding",
            entity_id=str(entity_id),
            entity_type=entity_type,
            dimensions=len(embedding),
        )

    async def search_similar(
        self,
        embedding: list[float],
        entity_type: str | None = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[dict]:
        """Search similar embeddings using pgvector cosine similarity."""
        try:
            results = await _pg_cosine_search(embedding, limit=limit)
            logger.info(
                "pgvector_search_similar",
                entity_type=entity_type,
                results=len(results),
            )
            return [
                {"entity_id": r, "entity_type": entity_type or "unknown", "score": 0.0}
                for r in results
            ]
        except Exception as e:
            logger.error("pgvector_search_failed", error=str(e))
            return []

    async def delete_embedding(self, entity_id: uuid.UUID, entity_type: str) -> None:
        """Delete handled by repository layer when entity is deleted."""
        logger.info(
            "pgvector_delete_embedding",
            entity_id=str(entity_id),
            entity_type=entity_type,
        )
