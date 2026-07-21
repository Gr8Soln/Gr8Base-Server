"""Integration tests for Career Profile Engine API."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestCareerRoutes:
    @pytest.mark.asyncio
    async def test_get_profile_unauthenticated(self, client):
        response = await client.get("/api/v1/career/profile")
        assert response.status_code == 403  # No auth header

    @pytest.mark.asyncio
    async def test_ingest_unauthenticated(self, client):
        response = await client.post("/api/v1/career/ingest")
        assert response.status_code == 403  # No auth header
