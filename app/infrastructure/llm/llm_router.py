from enum import StrEnum
from typing import Any

import litellm

from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)

settings = get_settings()

litellm.set_verbose = settings.debug


class LLMModel(StrEnum):
    PRIMARY = settings.llm_primary_model
    FALLBACK = settings.llm_fallback_model


async def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    response_format: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Any:
    target_model = model or settings.llm_primary_model

    try:
        response = await litellm.acompletion(
            model=target_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            api_key=_get_api_key(target_model),
            **kwargs,
        )
        logger.info("llm_call_success", model=target_model, tokens=response.usage.total_tokens)
        return response

    except Exception as e:
        logger.warning("llm_primary_failed", model=target_model, error=str(e))

        if target_model != settings.llm_fallback_model:
            logger.info("llm_falling_back", fallback=settings.llm_fallback_model)
            return await chat_completion(
                messages=messages,
                model=settings.llm_fallback_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        raise


def _get_api_key(model: str) -> str:
    if model.startswith("claude"):
        return settings.anthropic_api_key
    return settings.openai_api_key
