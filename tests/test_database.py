"""Unit tests for database module."""

import pytest

import app.database as db_module
from app.database import get_db, init_db


@pytest.mark.asyncio
async def test_wal_mode(db):
    """Database connections use WAL journal mode."""
    cursor = await db.execute("PRAGMA journal_mode")
    row = await cursor.fetchone()
    assert row[0] == "wal"


@pytest.mark.asyncio
async def test_foreign_keys_on(db):
    """Database connections enforce foreign keys."""
    cursor = await db.execute("PRAGMA foreign_keys")
    row = await cursor.fetchone()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_tables_created(db):
    """init_db creates properties and assets tables."""
    cursor = await db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    rows = await cursor.fetchall()
    table_names = {row[0] for row in rows}
    assert "properties" in table_names
    assert "assets" in table_names


@pytest.mark.asyncio
async def test_properties_schema(db):
    """Properties table has expected columns."""
    cursor = await db.execute("PRAGMA table_info(properties)")
    rows = await cursor.fetchall()
    columns = {row[1] for row in rows}
    assert columns == {"id", "name", "address", "created_at"}


@pytest.mark.asyncio
async def test_assets_schema(db):
    """Assets table has expected columns."""
    cursor = await db.execute("PRAGMA table_info(assets)")
    rows = await cursor.fetchall()
    columns = {row[1] for row in rows}
    assert columns == {
        "id", "property_id", "filename", "file_type",
        "mime_type", "gcs_uri", "embedded", "created_at",
    }


@pytest.mark.asyncio
async def test_cascade_delete(db):
    """Deleting a property cascades to delete its assets."""
    await db.execute(
        "INSERT INTO properties (id, name, address) VALUES (?, ?, ?)",
        ("p1", "Test Property", "123 Main St"),
    )
    await db.execute(
        "INSERT INTO assets (id, property_id, filename) VALUES (?, ?, ?)",
        ("a1", "p1", "photo.jpg"),
    )
    await db.commit()

    # Delete the property
    await db.execute("DELETE FROM properties WHERE id = ?", ("p1",))
    await db.commit()

    # Asset should be gone via cascade
    cursor = await db.execute("SELECT COUNT(*) FROM assets WHERE id = ?", ("a1",))
    row = await cursor.fetchone()
    assert row[0] == 0
