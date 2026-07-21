import uuid
from abc import ABC, abstractmethod


class VectorStorePort(ABC):
    """Abstract port for vector storage and similarity search.

    Provider-independent — supports pgvector, Pinecone, Qdrant, Weaviate, Milvus.
    """

    @abstractmethod
    async def store_embedding(
        self,
        entity_id: uuid.UUID,
        embedding: list[float],
        entity_type: str,
        metadata: dict | None = None,
    ) -> None:
        """Store an embedding vector for an entity."""
        ...

    @abstractmethod
    async def search_similar(
        self,
        embedding: list[float],
        entity_type: str | None = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[dict]:
        """Find entities with similar embeddings via cosine similarity."""
        ...

    @abstractmethod
    async def delete_embedding(self, entity_id: uuid.UUID, entity_type: str) -> None:
        """Remove an embedding from the store."""
        ...
