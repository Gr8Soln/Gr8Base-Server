from abc import ABC, abstractmethod


class EmbeddingProviderPort(ABC):
    """Abstract port for embedding generation.

    Provider-independent — supports OpenAI, Cohere, Voyage, etc.
    """

    @abstractmethod
    async def generate_embedding(self, text: str, model: str | None = None) -> list[float]:
        """Generate a single embedding vector for the given text."""
        ...

    @abstractmethod
    async def generate_embeddings(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts in one batch."""
        ...

    @abstractmethod
    def get_dimensions(self) -> int:
        """Return the embedding vector dimensions for the current model."""
        ...
