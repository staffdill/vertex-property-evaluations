"""Shared test fixtures."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

import app.database as db_module
from app.database import init_db
from app.main import app


@pytest_asyncio.fixture
async def client(tmp_path, monkeypatch):
    """Create test client with isolated temp database."""
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db(tmp_path, monkeypatch):
    """Provide an isolated database connection for unit tests."""
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    await init_db()
    conn = await db_module.get_db()
    try:
        yield conn
    finally:
        await conn.close()
