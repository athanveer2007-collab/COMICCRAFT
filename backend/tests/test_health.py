"""Tests for the health check endpoint and error handlers."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """Ensure GET /api/v1/health returns 200 with valid schema."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "storage_writable" in data
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_not_found_returns_error_envelope(client: AsyncClient) -> None:
    """Ensure missing endpoint returns 404 with standard error envelope."""
    response = await client.get("/api/v1/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]


@pytest.mark.asyncio
async def test_dev_endpoint_disabled_in_production(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure dev test image endpoint is forbidden in production."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    response = await client.post("/api/v1/dev/test-image", json={"prompt": "test"})
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"
