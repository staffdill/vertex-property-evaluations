"""Asset router — stub for Phase 3 file upload integration."""
import aiosqlite
from fastapi import APIRouter, Depends
from app.database import get_db
from app.models import AssetResponse

router = APIRouter(prefix="/api/properties", tags=["assets"])


async def get_connection():
    conn = await get_db()
    try:
        yield conn
    finally:
        await conn.close()


@router.get("/{property_id}/assets")
async def list_assets(
    property_id: str,
    conn: aiosqlite.Connection = Depends(get_connection),
):
    """Return assets for a property. Phase 3 will add POST and DELETE."""
    cursor = await conn.execute(
        "SELECT id, property_id, filename, file_type, mime_type, gcs_uri, embedded, created_at "
        "FROM assets WHERE property_id = ? ORDER BY created_at DESC",
        (property_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]
