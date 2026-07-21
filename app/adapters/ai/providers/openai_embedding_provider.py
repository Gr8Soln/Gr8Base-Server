from app.application.ports.ai.embedding_provider_port import EmbeddingProviderPort
from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.vector.embedding_service import generate_embedding as _generate

logger = get_logger(__name__)
settings = get_settings()


class OpenAIEmbeddingProvider(EmbeddingProviderPort):
    """OpenAI embedding provider adapter.

    Wraps the existing embedding_service.py for the port interface.
    Future providers (Cohere, Voyage) can be added alongside this one.
    """

    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.embedding_model

    async def generate_embedding(self, text: str, model: str | None = None) -> list[float]:
        target_model = model or self._model
        logger.info("embedding_generate", model=target_model, text_length=len(text))
        return await _generate(text[:30000])

    async def generate_embeddings(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        # Sequential for now; can be parallelized later
        results: list[list[float]] = []
        for text in texts:
            results.append(await self.generate_embedding(text, model=model))
        return results

    def get_dimensions(self) -> int:
        return 1536  # text-embedding-3-small
