# Phase 2: Property CRUD - Research

**Researched:** 2026-03-11
**Domain:** FastAPI routers, Pydantic models, SQLite CRUD with aiosqlite, cascade delete strategy
**Confidence:** HIGH

## Summary

Phase 2 builds the working API endpoints for property dossier management on top of the Phase 1 skeleton. The schema is already live in `db/wise.db` with both `properties` and `assets` tables. The task is to write route handlers that create, list, read, and delete properties, backed by raw aiosqlite SQL that matches the existing schema exactly.

The architecture research already defined the target structure: `app/routers/properties.py` for route handlers, `app/models.py` for Pydantic request/response shapes, and `app/main.py` updated to `include_router`. No new dependencies are needed for the core CRUD work -- everything required (FastAPI, aiosqlite, Pydantic) is already in the venv. The cascade delete success criterion mentions ChromaDB and GCS, but because no files are uploaded until Phase 3 and no embeddings are created until Phase 4, those stores will be empty in Phase 2. The SQLite `ON DELETE CASCADE` foreign key (already in the schema) handles the only real cascade needed here.

The user instruction adds "file upload logic for property images" to this phase. This is interpreted as creating the `asset` CRUD foundation (create asset record, list assets for a property, delete asset) rather than the actual GCS signed-URL upload flow, which belongs to Phase 3. The wise.db schema already has the `assets` table with all columns needed.

**Primary recommendation:** Use FastAPI `APIRouter`, write `app/routers/properties.py` and `app/models.py`, add `app/routers/assets.py` for asset record CRUD, update `app/main.py` to register the routers before the StaticFiles mount. All data access via raw aiosqlite SQL matching the existing schema.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROP-01 | User can create a property dossier with name and address | POST /api/properties -- INSERT into properties table, uuid4 id, return created record |
| PROP-02 | User can view a list of all properties with file counts and risk badges | GET /api/properties -- SELECT properties LEFT JOIN assets COUNT, risk badge is None/null until Phase 5 |
| PROP-03 | User can view property details with all associated assets | GET /api/properties/{id} -- SELECT property + SELECT assets WHERE property_id |
| PROP-04 | User can delete a property, cascading removal from SQLite, ChromaDB, and GCS | DELETE /api/properties/{id} -- SQLite ON DELETE CASCADE handles assets; ChromaDB/GCS are empty in Phase 2, service stubs log intent |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.1 | APIRouter, HTTPException, Depends | Already in venv. Routers clean up main.py. |
| aiosqlite | 0.22.1 | Async SQLite queries | Already in venv. Must use for all DB access -- no sync sqlite3 in async handlers. |
| Pydantic | 2.12.5 | Request/response models, input validation | Already in venv. FastAPI uses it natively for JSON serialization. |
| uuid (stdlib) | builtin | Generate property and asset IDs | No external dep needed. `uuid.uuid4().hex` is collision-proof. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | latest | Form data / file upload body parsing | Required by FastAPI for any `Form()` or `UploadFile` parameters. NOT in venv yet -- must install for Phase 2 if asset endpoints use Form. For JSON-only CRUD, not strictly required. |
| datetime (stdlib) | builtin | created_at timestamps | `datetime.utcnow().isoformat()` as fallback; SQLite DEFAULT handles it in schema. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw aiosqlite SQL | SQLAlchemy ORM | 2 tables. ORM adds abstraction without value. Raw SQL is faster to read and debug. Consistent with project research decision. |
| `uuid.uuid4().hex` | `nanoid` / `cuid` | uuid4.hex is stdlib, URL-safe, collision-proof. No reason to add a dependency. |
| JSON body for create | Form data for create | JSON body matches REST convention. Form data is for file uploads (Phase 3). Keep CRUD as JSON. |

**Installation:**
```bash
# Nothing new needed for core CRUD.
# Install python-multipart only if asset endpoints in this phase use Form:
./venv/bin/pip install python-multipart
```

## Architecture Patterns

### Recommended Project Structure (Phase 2 additions)

```
vertex-property-evaluations/
  app/
    __init__.py
    main.py              # Updated: include routers before StaticFiles mount
    config.py            # No changes
    database.py          # No changes
    models.py            # NEW: Pydantic request/response models
    routers/
      __init__.py        # NEW: empty package marker
      properties.py      # NEW: property CRUD endpoints
      assets.py          # NEW: asset record CRUD (stub for Phase 3 upload logic)
  tests/
    test_properties.py   # NEW: property CRUD endpoint tests
    test_assets.py       # NEW: asset CRUD tests (optional in this phase)
```

### Pattern 1: FastAPI APIRouter Registration Order

**What:** Define routes in separate files using `APIRouter`, then `include_router` in `main.py` BEFORE the StaticFiles mount.
**When to use:** Always -- route ordering is critical. StaticFiles at "/" catches everything if registered first.

```python
# app/main.py
from app.routers import properties, assets

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Wise Evaluations", lifespan=lifespan)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

# API routers -- BEFORE static mount
app.include_router(properties.router)
app.include_router(assets.router)

# StaticFiles LAST
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### Pattern 2: Property Router with get_db Dependency

**What:** Use FastAPI `Depends` to inject the database connection. Always close the connection in a `finally` block.
**When to use:** Every route handler that needs database access.

```python
# app/routers/properties.py
from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
import aiosqlite

router = APIRouter(prefix="/api/properties", tags=["properties"])

async def get_connection():
    conn = await get_db()
    try:
        yield conn
    finally:
        await conn.close()

@router.post("/", status_code=201)
async def create_property(
    body: PropertyCreate,
    conn: aiosqlite.Connection = Depends(get_connection)
):
    prop_id = uuid.uuid4().hex
    await conn.execute(
        "INSERT INTO properties (id, name, address) VALUES (?, ?, ?)",
        (prop_id, body.name, body.address)
    )
    await conn.commit()
    row = await conn.execute(
        "SELECT id, name, address, created_at FROM properties WHERE id = ?",
        (prop_id,)
    )
    record = await row.fetchone()
    return dict(record)
```

### Pattern 3: Property List with Asset Count

**What:** Use LEFT JOIN + GROUP BY to return asset count alongside each property. Risk badge is `null` until Phase 5 produces analysis results.
**When to use:** GET /api/properties

```python
@router.get("/")
async def list_properties(conn: aiosqlite.Connection = Depends(get_connection)):
    cursor = await conn.execute("""
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
    """)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
```

### Pattern 4: Delete with Cascade

**What:** DELETE from properties table. SQLite's `ON DELETE CASCADE` (already in schema + `PRAGMA foreign_keys=ON`) automatically deletes child assets rows. No manual asset deletion needed in SQL. ChromaDB and GCS are empty in Phase 2 -- service stubs handle intent.
**When to use:** DELETE /api/properties/{id}

```python
@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: str,
    conn: aiosqlite.Connection = Depends(get_connection)
):
    # Check exists first to return proper 404
    cursor = await conn.execute(
        "SELECT id FROM properties WHERE id = ?", (property_id,)
    )
    if await cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # foreign_keys=ON + ON DELETE CASCADE removes assets automatically
    await conn.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    await conn.commit()
    # ChromaDB/GCS cleanup: no-op in Phase 2 (no files exist yet)
    # Phase 4 will add: await chroma_service.delete_by_property(property_id)
    # Phase 3 will add: await gcs_service.delete_prefix(f"{property_id}/")
```

### Pattern 5: Pydantic Models

**What:** Separate request models (what comes in) from response models (what goes out). Use `model_config` for orm-mode-style dict access.
**When to use:** All endpoints.

```python
# app/models.py
from pydantic import BaseModel, Field
from typing import Optional

class PropertyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)

class PropertyResponse(BaseModel):
    id: str
    name: str
    address: str
    created_at: str
    asset_count: int = 0
    risk_badge: Optional[str] = None  # null until Phase 5

class AssetResponse(BaseModel):
    id: str
    property_id: str
    filename: Optional[str] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    gcs_uri: Optional[str] = None
    embedded: int = 0
    created_at: str
```

### Anti-Patterns to Avoid

- **Calling `get_db()` without a try/finally:** Leaves SQLite connections open. Use `Depends(get_connection)` which wraps the lifecycle properly.
- **Checking `PRAGMA foreign_keys` per-request:** It is already set in `get_db()`. Do not duplicate it in router code.
- **Returning aiosqlite.Row objects directly:** FastAPI cannot serialize them. Always `dict(row)` or use Pydantic model_validate.
- **Deleting assets manually before deleting the property:** Redundant if `ON DELETE CASCADE` is in place and `foreign_keys=ON` is set. The Phase 1 schema already has both.
- **Using 200 for create:** Use `status_code=201`. Use `204` for successful delete with no body.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Input validation | Manual `if not name:` checks | Pydantic `Field(min_length=1)` | Pydantic generates 422 with field-level error details automatically |
| UUID generation | `random.randint` or timestamp | `uuid.uuid4().hex` | Collision-proof, stdlib, URL-safe |
| Connection lifecycle | Manual open/close in each handler | `Depends(get_connection)` generator | Centralizes cleanup, runs even on exceptions |
| Route prefixing | `/api/properties/` hardcoded in each route | `APIRouter(prefix="/api/properties")` | Single source of truth for path prefix |

**Key insight:** FastAPI's dependency injection via `Depends` is the right tool for database connection lifecycle. Do not manage open/close manually in each handler.

## Common Pitfalls

### Pitfall 1: aiosqlite.Row is Not JSON-Serializable

**What goes wrong:** Returning `row` directly from an endpoint causes FastAPI to raise a serialization error or return an empty object.
**Why it happens:** `aiosqlite.Row` is a sqlite3.Row-compatible object. FastAPI's JSON encoder does not know how to serialize it.
**How to avoid:** Always convert: `dict(row)`, `[dict(r) for r in rows]`, or use `PropertyResponse.model_validate(dict(row))`.
**Warning signs:** `TypeError: Object of type Row is not JSON serializable` in server logs.

### Pitfall 2: get_db() Called Without Closing

**What goes wrong:** SQLite connections accumulate. Under test load or rapid requests, SQLite hits its connection limit or "database is locked" errors appear.
**Why it happens:** `await get_db()` returns a raw connection. If the handler raises before `await conn.close()`, the connection leaks.
**How to avoid:** Use a `Depends(get_connection)` generator with `try/yield/finally`. The finally block runs on exception too.

### Pitfall 3: foreign_keys Pragma Not Active at Delete Time

**What goes wrong:** DELETE from properties does not cascade to assets. Orphaned asset rows remain.
**Why it happens:** `PRAGMA foreign_keys=ON` is per-connection and is set in `get_db()`. If any code path creates a connection without calling `get_db()` (e.g., a direct `aiosqlite.connect()` call), foreign keys are silently disabled.
**How to avoid:** Always use `get_db()` exclusively. Never call `aiosqlite.connect()` directly in route handlers.
**Warning signs:** After DELETE property, `SELECT * FROM assets WHERE property_id = ?` still returns rows.

### Pitfall 4: 404 vs 204 on Delete

**What goes wrong:** Deleting a non-existent property returns 204 (silent success) instead of 404.
**Why it happens:** `DELETE FROM properties WHERE id = ?` succeeds even when no row matches. `rowcount` is 0 but the command doesn't error.
**How to avoid:** Check existence first with a `SELECT id FROM properties WHERE id = ?`, raise `HTTPException(404)` if not found, then delete.

### Pitfall 5: StaticFiles Catch-All Eating API Routes

**What goes wrong:** New router endpoints return HTML 404 instead of JSON.
**Why it happens:** `include_router` called AFTER `app.mount("/", StaticFiles(...))` in main.py. StaticFiles catches the request first.
**How to avoid:** Always add `include_router` calls before the StaticFiles mount line. This was already an established invariant from Phase 1.

### Pitfall 6: ChromaDB/GCS Not Installed

**What goes wrong:** If Phase 2 imports from `app.services.gcs` or `app.services.embedding` and those modules import `chromadb` or `google.cloud.storage`, import will fail -- neither library is in the current venv.
**Why it happens:** The project research noted these as "already installed" but the actual venv (`./venv/bin/pip list`) only has 26 packages. ChromaDB and GCS client are not present.
**How to avoid:** Phase 2 MUST NOT import chromadb or google-cloud-storage. Keep cascade delete as a SQLite-only operation. Service stub files for GCS/ChromaDB should be created as placeholder modules with `TODO` comments but must not be imported at module load time.

## Code Examples

Verified patterns for this project's existing stack:

### Create Property Endpoint

```python
# app/routers/properties.py
import uuid
from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
from app.database import get_db
from app.models import PropertyCreate

router = APIRouter(prefix="/api/properties", tags=["properties"])

async def get_connection():
    conn = await get_db()
    try:
        yield conn
    finally:
        await conn.close()

@router.post("/", status_code=201)
async def create_property(
    body: PropertyCreate,
    conn: aiosqlite.Connection = Depends(get_connection)
):
    prop_id = uuid.uuid4().hex
    await conn.execute(
        "INSERT INTO properties (id, name, address) VALUES (?, ?, ?)",
        (prop_id, body.name, body.address)
    )
    await conn.commit()
    cursor = await conn.execute(
        "SELECT id, name, address, created_at FROM properties WHERE id = ?",
        (prop_id,)
    )
    row = await cursor.fetchone()
    return dict(row)
```

### List Properties with Asset Count

```python
@router.get("/")
async def list_properties(conn: aiosqlite.Connection = Depends(get_connection)):
    cursor = await conn.execute("""
        SELECT
            p.id, p.name, p.address, p.created_at,
            COUNT(a.id) AS asset_count,
            NULL AS risk_badge
        FROM properties p
        LEFT JOIN assets a ON a.property_id = p.id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
```

### Get Single Property with Assets

```python
@router.get("/{property_id}")
async def get_property(
    property_id: str,
    conn: aiosqlite.Connection = Depends(get_connection)
):
    cursor = await conn.execute(
        "SELECT id, name, address, created_at FROM properties WHERE id = ?",
        (property_id,)
    )
    row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Property not found")

    cursor2 = await conn.execute(
        "SELECT id, property_id, filename, file_type, mime_type, gcs_uri, embedded, created_at "
        "FROM assets WHERE property_id = ? ORDER BY created_at DESC",
        (property_id,)
    )
    assets = await cursor2.fetchall()
    result = dict(row)
    result["assets"] = [dict(a) for a in assets]
    return result
```

### Delete Property

```python
@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: str,
    conn: aiosqlite.Connection = Depends(get_connection)
):
    cursor = await conn.execute(
        "SELECT id FROM properties WHERE id = ?", (property_id,)
    )
    if await cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Property not found")

    await conn.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    await conn.commit()
    # Phase 3+: gcs_service.delete_prefix(f"{property_id}/")
    # Phase 4+: chroma_service.delete_by_property(property_id)
```

### Test Pattern for CRUD Endpoints

```python
# tests/test_properties.py
import pytest

@pytest.mark.asyncio
async def test_create_property(client):
    response = await client.post("/api/properties/", json={
        "name": "1847 Ridgeline Dr",
        "address": "1847 Ridgeline Drive, Austin TX 78701"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "1847 Ridgeline Dr"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_properties(client):
    await client.post("/api/properties/", json={"name": "A", "address": "123 Main St"})
    response = await client.get("/api/properties/")
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_delete_cascades(client):
    resp = await client.post("/api/properties/", json={"name": "A", "address": "123 St"})
    prop_id = resp.json()["id"]
    del_resp = await client.delete(f"/api/properties/{prop_id}")
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/api/properties/{prop_id}")
    assert get_resp.status_code == 404
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` | `lifespan` context manager | FastAPI 0.93+ (2023) | Already using lifespan. No change. |
| `response_model=` with ORM mode | `dict(row)` + Pydantic `model_validate` | Pydantic v2 | `orm_mode` renamed to `from_attributes=True`. Use `dict(row)` for simplicity with aiosqlite.Row. |
| `@app.get` on main app | `APIRouter` with `include_router` | FastAPI 0.x | Routers are the standard way to organize multi-file FastAPI apps. |

**Deprecated/outdated:**
- `orm_mode = True` (Pydantic v1): Use `model_config = ConfigDict(from_attributes=True)` in Pydantic v2 if needed. For aiosqlite.Row, `dict(row)` is simpler.

## Open Questions

1. **Cascade delete scope in Phase 2**
   - What we know: SQLite ON DELETE CASCADE is active. ChromaDB and GCS are not installed.
   - What's unclear: Should Phase 2 create empty stub service modules (`app/services/gcs.py`, `app/services/embedding.py`) as placeholders?
   - Recommendation: YES -- create stub files with `# TODO Phase 3/4` comments and `pass` implementations. This establishes the module path so Phase 3/4 can fill them in without touching main.py. But do NOT import them in route handlers yet (avoids import errors).

2. **PROP-02 risk badge**
   - What we know: Requirements say "file counts and risk badges" but analysis doesn't exist until Phase 5.
   - What's unclear: Should the list endpoint return `risk_badge: null` or omit the field?
   - Recommendation: Return `risk_badge: null` explicitly. Frontend can treat null as "no assessment yet." Consistent schema from the start avoids breaking frontend changes in Phase 5.

3. **python-multipart install**
   - What we know: FastAPI requires python-multipart for any Form() or UploadFile parameters. Phase 2 uses JSON bodies only.
   - What's unclear: If the user instruction "add file upload logic for property images" means UploadFile in Phase 2.
   - Recommendation: Treat Phase 2 as JSON-only CRUD. Install python-multipart as part of Phase 3 when UploadFile is actually needed. Avoids premature dependency.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| Config file | `pyproject.toml` (`asyncio_mode = "auto"`) |
| Quick run command | `./venv/bin/python -m pytest tests/ -x -q` |
| Full suite command | `./venv/bin/python -m pytest tests/ -v` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROP-01 | POST /api/properties creates record and returns 201 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_create_property -x` | Wave 0 |
| PROP-01 | POST with missing name returns 422 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_create_missing_fields -x` | Wave 0 |
| PROP-02 | GET /api/properties returns list with asset_count and risk_badge | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_list_properties -x` | Wave 0 |
| PROP-03 | GET /api/properties/{id} returns property with assets array | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_get_property -x` | Wave 0 |
| PROP-03 | GET /api/properties/{id} returns 404 for unknown id | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_get_property_not_found -x` | Wave 0 |
| PROP-04 | DELETE /api/properties/{id} returns 204 and removes record | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_delete_property -x` | Wave 0 |
| PROP-04 | DELETE cascades -- assets removed via FK | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_delete_cascades_assets -x` | Wave 0 |
| PROP-04 | DELETE non-existent returns 404 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_delete_not_found -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `./venv/bin/python -m pytest tests/ -x -q`
- **Per wave merge:** `./venv/bin/python -m pytest tests/ -v`
- **Phase gate:** All 9 original tests + all new property tests green before verification

### Wave 0 Gaps

- [ ] `app/routers/__init__.py` -- package marker
- [ ] `app/routers/properties.py` -- property CRUD router
- [ ] `app/routers/assets.py` -- asset record router (stub)
- [ ] `app/models.py` -- Pydantic models
- [ ] `tests/test_properties.py` -- covers PROP-01 through PROP-04
- [ ] Updated `app/main.py` -- include_router calls before StaticFiles mount

*(Existing test infrastructure in conftest.py, pyproject.toml, and tests/ is fully usable -- no framework gaps)*

## Sources

### Primary (HIGH confidence)

- `app/database.py` (local) -- verified exact schema: properties(id, name, address, created_at), assets(id, property_id, filename, file_type, mime_type, gcs_uri, embedded, created_at) with ON DELETE CASCADE
- `./venv/bin/pip list` (local, run 2026-03-11) -- verified installed packages: no ChromaDB, no google-cloud-storage, no google-genai in venv
- `.planning/research/ARCHITECTURE.md` (local) -- routers/properties.py, services/ structure, thin router pattern
- `.planning/research/STACK.md` (local) -- confirmed aiosqlite raw SQL over ORM decision
- [FastAPI APIRouter docs](https://fastapi.tiangolo.com/tutorial/bigger-applications/) -- include_router pattern, prefix, tags
- [FastAPI Dependencies docs](https://fastapi.tiangolo.com/tutorial/dependencies/) -- Depends() generator pattern for connection lifecycle

### Secondary (MEDIUM confidence)

- `.planning/research/PITFALLS.md` (local) -- Pitfall 10: GCS object orphans on delete, deletion order
- Phase 1 tests (local) -- conftest.py `client` fixture with `monkeypatch` verified reusable for Phase 2

### Tertiary (LOW confidence)

- None -- all critical findings verified against local files and official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already installed and verified via pip list
- Architecture: HIGH -- patterns defined in prior research, confirmed by existing Phase 1 code
- Pitfalls: HIGH -- aiosqlite.Row serialization, connection lifecycle, and foreign keys pragma are well-known FastAPI+SQLite behaviors; ChromaDB/GCS absence verified directly

**Research date:** 2026-03-11
**Valid until:** 2026-04-11 (stable stack; only risk is FastAPI/Pydantic minor updates)
