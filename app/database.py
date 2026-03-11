"""SQLite database initialization and connection factory."""

import aiosqlite

from app.config import settings

DB_PATH = settings.db_path


async def get_db() -> aiosqlite.Connection:
    """Return a connection with WAL mode and foreign keys enabled."""
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    return conn


async def init_db() -> None:
    """Create database directory and initialize schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await get_db()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL,
                filename TEXT,
                file_type TEXT,
                mime_type TEXT,
                gcs_uri TEXT,
                embedded INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
            )
        """)
        await conn.commit()
    finally:
        await conn.close()
