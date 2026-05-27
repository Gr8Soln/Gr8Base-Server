import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.api.dependencies.auth import get_current_user
from app.domain.entities.resume import Resume
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


def _make_resume(user_id: uuid.UUID) -> Resume:
    return Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="John Doe, Python Engineer",
        skills=["Python", "FastAPI"],
        version=1,
        label="",
    )


@pytest.mark.asyncio
async def test_list_resumes_returns_empty_for_new_user() -> None:
    user = _make_user()

    async def mock_auth() -> User:
        return user

    async def mock_repo_list(*args, **kwargs) -> list:
        return []

    app.dependency_overrides[get_current_user] = mock_auth

    with patch(
        "app.adapters.api.routes.resume_routes.PgResumeRepository"
    ) as mock_repo:
        instance = MagicMock()
        instance.get_by_user_id = AsyncMock(return_value=[])
        mock_repo.return_value = instance

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/resumes")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_resume_returns_404_for_unknown_id() -> None:
    user = _make_user()

    async def mock_auth() -> User:
        return user

    app.dependency_overrides[get_current_user] = mock_auth

    with patch(
        "app.adapters.api.routes.resume_routes.PgResumeRepository"
    ) as mock_repo:
        instance = MagicMock()
        instance.get_by_id = AsyncMock(return_value=None)
        mock_repo.return_value = instance

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/resumes/{uuid.uuid4()}")

    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_rejects_invalid_content_type() -> None:
    user = _make_user()

    async def mock_auth() -> User:
        return user

    app.dependency_overrides[get_current_user] = mock_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/resumes/upload",
            files={"file": ("photo.png", b"fake image bytes", "image/png")},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_resumes_endpoint_requires_auth() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/resumes")

    assert response.status_code == 401
