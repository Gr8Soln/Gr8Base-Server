import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.api.dependencies.auth import get_current_user
from app.domain.entities.job import JobDescription
from app.domain.entities.user import User
from app.infrastructure.security.password_handler import hash_password
from app.main import app


def _make_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="emmanuel@gr8soln.dev",
        hashed_password=hash_password("password123"),
        full_name="Emmanuel",
        is_active=True,
        is_verified=True,
    )


def _make_job(user_id: uuid.UUID) -> JobDescription:
    return JobDescription(
        id=uuid.uuid4(),
        user_id=user_id,
        raw_text="We need a Senior Backend Engineer...",
        title="Senior Backend Engineer",
        role="Backend Engineer",
        seniority="Senior",
        domain="Fintech",
        required_skills=["Python", "FastAPI"],
        ats_keywords=["python", "fastapi"],
    )


@pytest.mark.asyncio
async def test_list_jobs_returns_empty_for_new_user() -> None:
    user = _make_user()

    async def mock_auth() -> User:
        return user

    app.dependency_overrides[get_current_user] = mock_auth

    with patch("app.adapters.api.routes.job_routes.PgJobRepository") as mock_repo:
        instance = MagicMock()
        instance.get_by_user_id = AsyncMock(return_value=[])
        mock_repo.return_value = instance

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/jobs")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_job_returns_404_for_unknown_id() -> None:
    user = _make_user()

    async def mock_auth() -> User:
        return user

    app.dependency_overrides[get_current_user] = mock_auth

    with patch("app.adapters.api.routes.job_routes.PgJobRepository") as mock_repo:
        instance = MagicMock()
        instance.get_by_id = AsyncMock(return_value=None)
        mock_repo.return_value = instance

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/jobs/{uuid.uuid4()}")

    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jobs_endpoint_requires_auth() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/jobs")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_keywords_returns_deduplicated_list() -> None:
    user = _make_user()
    job = _make_job(user.id)

    async def mock_auth() -> User:
        return user

    app.dependency_overrides[get_current_user] = mock_auth

    with patch("app.adapters.api.routes.job_routes.PgJobRepository") as mock_repo:
        instance = MagicMock()
        instance.get_by_id = AsyncMock(return_value=job)
        mock_repo.return_value = instance

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/jobs/{job.id}/keywords")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert "keywords" in data
    assert "total" in data
    assert data["total"] == len(data["keywords"])
