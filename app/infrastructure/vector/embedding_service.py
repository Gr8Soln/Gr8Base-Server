from openai import AsyncOpenAI

from app.infrastructure.config.settings import settings
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)

_client: AsyncOpenAI | None = None
EMBEDDING_DIMENSIONS = 1536  # text-embedding-3-small


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generate_embedding(text: str) -> list[float]:
    """Generate a single embedding vector for the given text."""
    client = _get_client()

    # Truncate to stay within token limits (~8192 tokens)
    truncated = text[:30000]

    try:
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=truncated,
        )
        embedding = response.data[0].embedding
        logger.info(
            "embedding_generated",
            model=settings.embedding_model,
            dimensions=len(embedding),
            text_length=len(truncated),
        )
        return embedding
    except Exception as e:
        logger.error("embedding_generation_failed", error=str(e))
        raise


async def generate_resume_embedding(resume_text: str, skills: list[str]) -> list[float]:
    """Builds a semantically rich text for resume embedding."""
    combined = f"{resume_text}\n\nKey Skills: {', '.join(skills)}"
    return await generate_embedding(combined)


async def generate_job_embedding(raw_text: str, required_skills: list[str]) -> list[float]:
    """Builds a semantically rich text for JD embedding."""
    combined = f"{raw_text}\n\nRequired: {', '.join(required_skills)}"
    return await generate_embedding(combined)
