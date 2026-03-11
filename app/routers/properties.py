"""Property CRUD router."""

import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
import aiosqlite

from app.database import get_db
from app.models import PropertyCreate

router = APIRouter(prefix="/api/properties", tags=["properties"])


async def get_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yield a DB connection from get_db() and close it when done."""
    conn = await get_db()
    try:
        yield conn
    finally:
        await conn.close()


@router.post("/", status_code=201)
async def create_property(body: PropertyCreate, conn: aiosqlite.Connection = Depends(get_connection)):
    """Create a new property dossier."""
    prop_id = str(uuid.uuid4())
    await conn.execute(
        "INSERT INTO properties (id, name, address) VALUES (?, ?, ?)",
        (prop_id, body.name, body.address),
    )
    await conn.commit()
    async with conn.execute(
        "SELECT id, name, address, created_at FROM properties WHERE id = ?",
        (prop_id,),
    ) as cursor:
        row = await cursor.fetchone()
    return dict(row)


@router.get("/")
async def list_properties(conn: aiosqlite.Connection = Depends(get_connection)):
    """Return all properties with asset count and risk badge."""
    async with conn.execute(
        """
        SELECT
            p.id,
            p.name,
            p.address,
            p.created_at,
            COUNT(a.id) AS asset_count,
            NULL AS risk_badge
        FROM properties p
        LEFT JOIN assets a ON a.property_id = p.id
        GROUP BY p.id
        ORDER BY p.created_at DESC
        """
    ) as cursor:
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/{property_id}")
async def get_property(property_id: str, conn: aiosqlite.Connection = Depends(get_connection)):
    """Return a single property with its associated assets."""
    async with conn.execute(
        "SELECT id, name, address, created_at FROM properties WHERE id = ?",
        (property_id,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Property not found")
    result = dict(row)
    async with conn.execute(
        "SELECT id, property_id, filename, file_type, mime_type, gcs_uri, embedded, created_at FROM assets WHERE property_id = ?",
        (property_id,),
    ) as cursor:
        assets = await cursor.fetchall()
    result["assets"] = [dict(a) for a in assets]
    return result


@router.delete("/{property_id}", status_code=204)
async def delete_property(property_id: str, conn: aiosqlite.Connection = Depends(get_connection)):
    """Delete a property and cascade-remove its assets."""
    async with conn.execute(
        "SELECT id FROM properties WHERE id = ?",
        (property_id,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Property not found")
    await conn.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    await conn.commit()
    return Response(status_code=204)
