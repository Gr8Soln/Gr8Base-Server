from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class LLMProviderPort(ABC):
    """Abstract port for LLM provider operations.

    Supports structured extraction and chat completion across
    multiple providers: OpenAI, DeepSeek, Gemini, Claude, Grok.
    Provider selection is configuration-driven.
    """

    @abstractmethod
    async def extract_structured[T: BaseModel](
        self,
        response_model: type[T],
        messages: list[dict[str, str]],
        system: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        max_retries: int = 3,
    ) -> T:
        """Extract structured data using Instructor/LiteLLM."""
        ...

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        response_format: dict[str, Any] | None = None,
    ) -> Any:
        """Standard chat completion with optional JSON mode."""
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Return list of configured model identifiers."""
        ...
