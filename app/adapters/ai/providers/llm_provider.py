from typing import Any

from pydantic import BaseModel

from app.application.ports.ai.llm_provider_port import LLMProviderPort
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.instructor_client import extract_structured as _instructor_extract
from app.infrastructure.llm.llm_router import chat_completion as _llm_chat
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)
settings = get_settings()

# ── Provider model configuration ──────────────────────────────────────────────

PROVIDER_MODELS: dict[str, list[str]] = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    "deepseek": ["deepseek-v4-pro", "deepseek-v4-flash"],
    "gemini": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "claude": ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5"],
    "grok": ["grok-3"],
}


class LiteLLMProvider(LLMProviderPort):
    """LLM provider adapter wrapping LiteLLM and Instructor.

    All existing AI agents can be migrated to this adapter without
    changing their business logic — only the import changes.
    """

    def __init__(self, default_model: str | None = None) -> None:
        self._default_model = default_model or settings.llm_primary_model

    async def extract_structured[T: BaseModel](
        self,
        response_model: type[T],
        messages: list[dict[str, str]],
        system: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        max_retries: int = 3,
    ) -> T:
        target_model = model or self._default_model
        logger.info(
            "llm_extract_structured",
            model=target_model,
            response_model=response_model.__name__,
        )
        try:
            return await _instructor_extract(
                response_model=response_model,
                messages=messages,
                system=system,
                model=target_model,
                temperature=temperature,
                max_retries=max_retries,
            )
        except Exception:
            logger.warning("llm_extract_failed", model=target_model)
            raise

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        response_format: dict[str, Any] | None = None,
    ) -> Any:
        target_model = model or self._default_model
        logger.info("llm_chat_completion", model=target_model)
        return await _llm_chat(
            messages=messages,
            model=target_model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    def get_available_models(self) -> list[str]:
        result: list[str] = []
        for models in PROVIDER_MODELS.values():
            result.extend(models)
        return result

    @property
    def default_model(self) -> str:
        return self._default_model
