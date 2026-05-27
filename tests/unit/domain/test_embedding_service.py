from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.vector.embedding_service import (
    generate_embedding,
    generate_job_embedding,
    generate_resume_embedding,
)


def _mock_openai_response(dims: int = 1536) -> MagicMock:
    mock_data = MagicMock()
    mock_data.embedding = [0.1] * dims
    mock_response = MagicMock()
    mock_response.data = [mock_data]
    return mock_response


@pytest.mark.asyncio
async def test_generate_embedding_returns_vector() -> None:
    mock_response = _mock_openai_response()

    with patch(
        "app.infrastructure.vector.embedding_service._get_client"
    ) as mock_client_fn:
        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_client_fn.return_value = mock_client

        result = await generate_embedding("Python FastAPI developer with 5 years experience")

    assert len(result) == 1536
    assert all(isinstance(v, float) for v in result)


@pytest.mark.asyncio
async def test_generate_resume_embedding_combines_text_and_skills() -> None:
    mock_response = _mock_openai_response()

    with patch(
        "app.infrastructure.vector.embedding_service._get_client"
    ) as mock_client_fn:
        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_client_fn.return_value = mock_client

        result = await generate_resume_embedding(
            "John Doe, Senior Engineer", ["Python", "FastAPI", "PostgreSQL"]
        )

        call_args = mock_client.embeddings.create.call_args
        input_text = call_args.kwargs.get("input") or call_args.args[0]
        assert "Python" in input_text
        assert "FastAPI" in input_text

    assert len(result) == 1536


@pytest.mark.asyncio
async def test_generate_job_embedding_combines_text_and_requirements() -> None:
    mock_response = _mock_openai_response()

    with patch(
        "app.infrastructure.vector.embedding_service._get_client"
    ) as mock_client_fn:
        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_client_fn.return_value = mock_client

        result = await generate_job_embedding(
            "Senior Backend Engineer role", ["Python", "Docker"]
        )

        call_args = mock_client.embeddings.create.call_args
        input_text = call_args.kwargs.get("input") or call_args.args[0]
        assert "Python" in input_text
        assert "Docker" in input_text

    assert len(result) == 1536


@pytest.mark.asyncio
async def test_generate_embedding_truncates_long_text() -> None:
    long_text = "x" * 50000  # exceeds 30k char limit
    mock_response = _mock_openai_response()

    with patch(
        "app.infrastructure.vector.embedding_service._get_client"
    ) as mock_client_fn:
        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_client_fn.return_value = mock_client

        await generate_embedding(long_text)

        call_args = mock_client.embeddings.create.call_args
        input_text = call_args.kwargs.get("input") or call_args.args[0]
        assert len(input_text) <= 30000
