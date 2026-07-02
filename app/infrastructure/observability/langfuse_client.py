from langfuse import Langfuse

from app.infrastructure.config.settings import settings

_langfuse_client: Langfuse | None = None


def get_langfuse() -> Langfuse | None:
    global _langfuse_client

    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None

    if _langfuse_client is None:
        _langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )

    return _langfuse_client
