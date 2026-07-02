"""
Instructor client — enforces structured Pydantic outputs from LLMs.
This is the primary interface for all AI agents.
"""

import instructor
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.infrastructure.config.settings import get_settings

settings = get_settings()
type ResponseModel[T: BaseModel] = T

_openai_instructor: instructor.AsyncInstructor | None = None
_anthropic_instructor: instructor.AsyncInstructor | None = None


def get_openai_instructor() -> instructor.AsyncInstructor:
    global _openai_instructor
    if _openai_instructor is None:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        _openai_instructor = instructor.from_openai(client)
    return _openai_instructor


def get_anthropic_instructor() -> instructor.AsyncInstructor:
    global _anthropic_instructor
    if _anthropic_instructor is None:
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        _anthropic_instructor = instructor.from_anthropic(client)
    return _anthropic_instructor


async def extract_structured[T: BaseModel](
    response_model: type[T],
    messages: list[dict[str, str]],
    system: str | None = None,
    model: str | None = None,
    max_retries: int = 3,
    temperature: float = 0.0,
) -> T:
    """
    Primary entrypoint for all structured AI extraction.
    Automatically retries until the response matches the Pydantic schema.
    """
    target_model = model or settings.llm_primary_model
    use_anthropic = target_model.startswith("claude")

    all_messages = messages
    if system and not use_anthropic:
        all_messages = [{"role": "system", "content": system}, *messages]

    if use_anthropic:
        client = get_anthropic_instructor()
        return await client.messages.create(
            model=target_model,
            response_model=response_model,
            messages=all_messages,
            system=system or "",
            max_tokens=4096,
            max_retries=max_retries,
        )
    else:
        client = get_openai_instructor()
        return await client.chat.completions.create(
            model=target_model,
            response_model=response_model,
            messages=all_messages,
            temperature=temperature,
            max_retries=max_retries,
        )
