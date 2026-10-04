"""Pytest configuration and shared test fixtures."""

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

# Set test environment before loading application
os.environ["ENVIRONMENT"] = "test"
os.environ["GOOGLE_API_KEY"] = "mock_test_key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client bound to ASGI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
