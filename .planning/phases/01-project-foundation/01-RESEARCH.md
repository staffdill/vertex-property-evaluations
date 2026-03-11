# Phase 1: Project Foundation - Research

**Researched:** 2026-03-10
**Domain:** FastAPI skeleton, SQLite schema, static file serving, dark theme CSS
**Confidence:** HIGH

## Summary

Phase 1 establishes the running application skeleton that all subsequent phases build on. The deliverable is a FastAPI dev server at localhost:8000 that serves static HTML with a dark theme, initializes a SQLite database with WAL mode and the core schema (properties + assets tables), and responds to a health check endpoint. No AI, no GCS, no ChromaDB -- just the foundation.

The stack is fully validated by prior project research. FastAPI with StaticFiles serves both API routes and the vanilla HTML/CSS/JS frontend from a single origin (no CORS needed). aiosqlite provides async SQLite access. The database schema must include both tables now so Phase 2 (Property CRUD) can immediately write endpoints against them.

**Primary recommendation:** Create `app/database.py` with WAL mode and schema init, `app/main.py` with StaticFiles mount at root and health check at `/api/health`, a `.gitignore`, and `requirements.txt`. Keep it minimal -- no routers or services yet.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FRNT-03 | Dark theme professional aesthetic served by FastAPI StaticFiles | StaticFiles `html=True` mount pattern, CSS custom properties for dark theme, verified project structure |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.115.0 | API framework + static file serving | Async-native, Pydantic v2, StaticFiles built-in. Already selected in project stack research. |
| uvicorn | 0.41.0 | ASGI dev server | Standard FastAPI companion. Use `uvicorn[standard]` for lifespan support. |
| aiosqlite | 0.22.1 | Async SQLite access | Non-blocking SQLite in async handlers. Prevents event loop blocking (Pitfall 4 in architecture research). |
| Python | 3.13.7 | Runtime | System Python version on this machine. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | 2.12.5 | Request/response models | Already installed. Used implicitly by FastAPI. |
| pydantic-settings | 2.13.1 | Config from env vars | Load database path, debug mode from environment. |
| pytest | latest | Test framework | Health check and DB init smoke tests. |
| pytest-asyncio | latest | Async test support | Testing async database functions. |
| httpx | 0.28.1 | Test client | FastAPI's async test client uses httpx. Already installed. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| aiosqlite raw SQL | SQLAlchemy ORM | 2 tables, 5 columns each. ORM adds abstraction without value. Raw SQL is clearer. |
| CSS custom properties | Tailwind/Bootstrap | 2 screens total. Custom dark theme is ~100 lines of CSS. No build tooling needed. |

**Installation:**
```bash
# From project root with venv activated:
pip install "fastapi[standard]" aiosqlite pytest pytest-asyncio
pip freeze > requirements.txt
```

## Architecture Patterns

### Recommended Project Structure (Phase 1 scope only)

```
vertex-property-evaluations/
  app/
    __init__.py           # Empty, marks as package
    main.py               # FastAPI app, lifespan, StaticFiles mount, health check
    database.py           # SQLite schema, WAL mode, connection helper
    config.py             # Settings via pydantic-settings (DB path, debug flag)
  static/
    index.html            # Test page (becomes dashboard in Phase 7)
    css/
      styles.css          # Dark theme base CSS
    js/
      (empty for now)     # JS files added in later phases
  tests/
    __init__.py
    conftest.py           # Shared fixtures (test client, temp DB)
    test_health.py        # Health check endpoint test
    test_database.py      # Schema creation, WAL mode verification
  .gitignore
  requirements.txt
  run.py                  # uvicorn launcher script
```

### Pattern 1: Lifespan-Based Database Init

**What:** Use FastAPI's lifespan context manager to initialize the database on startup. Schema creation runs once, idempotently.
**When to use:** Always -- database must exist before any request handler runs.
**Example:**

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

Source: [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

### Pattern 2: StaticFiles with html=True at Root

**What:** Mount StaticFiles at "/" with `html=True` to serve `index.html` when user visits the root URL. API routes must be registered BEFORE the static mount (FastAPI checks routes in order).
**When to use:** When serving a vanilla HTML frontend alongside API endpoints from the same origin.
**Critical detail:** The `html=True` parameter makes StaticFiles serve `index.html` for directory paths (e.g., "/" serves "static/index.html"). Without it, "/" returns 404.

```python
# API routes FIRST (before static mount)
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Static mount LAST (catches everything else)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

Source: [FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/)

### Pattern 3: WAL Mode + aiosqlite Connection Factory

**What:** Enable WAL journal mode on every connection. Use `CREATE TABLE IF NOT EXISTS` for idempotent schema init.
**When to use:** Every database interaction in this project.

```python
# app/database.py
import aiosqlite
from pathlib import Path

DB_PATH = Path("db/wise.db")

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db

async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS properties (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            property_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            gcs_uri TEXT,
            embedded INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
        );
    """)
    await db.commit()
    await db.close()
```

Source: [SQLite WAL docs](https://sqlite.org/wal.html), [aiosqlite usage](https://pypi.org/project/aiosqlite/)

### Pattern 4: Dark Theme with CSS Custom Properties

**What:** Define all colors as CSS custom properties on `:root`. This makes theme changes trivial and keeps the entire color palette in one place.
**When to use:** From the very first CSS file. All phases build on these variables.

```css
/* static/css/styles.css */
:root {
    --bg-primary: #0f0f0f;
    --bg-secondary: #1a1a2e;
    --bg-card: #16213e;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent: #4fc3f7;
    --accent-hover: #81d4fa;
    --border: #2a2a4a;
    --risk-high: #ef5350;
    --risk-medium: #ffa726;
    --risk-low: #66bb6a;
    --font-main: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-main);
    line-height: 1.6;
    min-height: 100vh;
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }
```

### Anti-Patterns to Avoid

- **Mounting StaticFiles before API routes:** FastAPI matches routes in registration order. If StaticFiles is mounted at "/" first, it catches `/api/health` and returns 404. Always register API routes before the catch-all static mount.
- **Synchronous sqlite3 in async handlers:** Blocks the event loop. Use aiosqlite from day one. (Pitfall 6 from project research.)
- **Hardcoding colors in individual CSS rules:** Use CSS custom properties. Later phases add risk badges, severity dots, and status indicators that all reference the same palette.
- **Forgetting `foreign_keys=ON`:** SQLite does not enforce foreign keys by default. Without this pragma, deleting a property leaves orphaned assets.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Static file serving | Custom route handler reading files from disk | `StaticFiles(directory="static", html=True)` | Handles MIME types, caching headers, 404s, directory index |
| Async SQLite | `asyncio.to_thread(sqlite3.connect, ...)` wrapper | `aiosqlite` | Proper connection pooling, context managers, Row factory |
| Config from env vars | `os.getenv()` scattered everywhere | `pydantic-settings` BaseSettings | Type validation, .env file support, single source of truth |
| UUID generation | `random.randint` or custom ID scheme | `uuid.uuid4().hex` | Collision-proof, standard, no external dependency |

## Common Pitfalls

### Pitfall 1: StaticFiles Mount Order
**What goes wrong:** API routes return 404 because StaticFiles mounted at "/" catches them first.
**Why it happens:** FastAPI/Starlette processes mounts and routes in registration order.
**How to avoid:** Register all API routes (or include routers) BEFORE `app.mount("/", StaticFiles(...))`.
**Warning signs:** `/api/health` returns HTML 404 page instead of JSON.

### Pitfall 2: SQLite WAL Mode Not Persisting
**What goes wrong:** WAL mode set on one connection but not on subsequent connections.
**Why it happens:** WAL mode persists in the database file after first set, BUT `PRAGMA foreign_keys=ON` does NOT persist. Developers assume all pragmas behave the same.
**How to avoid:** Run both `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` on every new connection. WAL is idempotent if already set.
**Warning signs:** Property delete does not cascade to assets table.

### Pitfall 3: Database Directory Not Created
**What goes wrong:** `aiosqlite.connect("db/wise.db")` fails because `db/` directory does not exist.
**Why it happens:** SQLite creates the file but not parent directories.
**How to avoid:** `Path("db").mkdir(parents=True, exist_ok=True)` in `init_db()`.
**Warning signs:** `FileNotFoundError` on first run.

### Pitfall 4: Missing `__init__.py` in app Package
**What goes wrong:** `from app.database import init_db` fails with `ModuleNotFoundError`.
**Why it happens:** Python requires `__init__.py` to treat directories as packages.
**How to avoid:** Create empty `__init__.py` in `app/` and `tests/`.
**Warning signs:** Import errors when running `uvicorn app.main:app`.

### Pitfall 5: `.gitignore` Missing Database and Credentials
**What goes wrong:** `db/wise.db`, `gcp-credentials.json`, or `data/chromadb/` committed to git.
**Why it happens:** Forgotten in initial setup. Once committed, removing from history is painful.
**How to avoid:** Create `.gitignore` in the very first commit with all data/credential paths.

## Code Examples

### Health Check Endpoint

```python
# app/main.py
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
```

### run.py Launcher

```python
# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### Test Page (index.html)

```html
<!-- static/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wise Evaluations</title>
    <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
    <header>
        <h1>Wise Evaluations</h1>
        <p>Multimodal Property Risk Assessment</p>
    </header>
    <main id="app">
        <p>Foundation loaded. Dashboard coming soon.</p>
    </main>
</body>
</html>
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
venv/
.venv/

# Database
db/
data/

# Credentials
gcp-credentials.json
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Test artifacts
.pytest_cache/
htmlcov/
.coverage
```

### conftest.py (Test Fixtures)

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, DB_PATH
from pathlib import Path
import tempfile

@pytest_asyncio.fixture
async def client(tmp_path, monkeypatch):
    # Use temp DB for tests
    test_db = tmp_path / "test.db"
    monkeypatch.setattr("app.database.DB_PATH", test_db)
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` | `lifespan` context manager | FastAPI 0.93+ (2023) | Startup/shutdown events are deprecated. Use lifespan. |
| `google-generativeai` SDK | `google-genai` SDK | Nov 2025 | Old SDK is dead. Not relevant to Phase 1 but noted for later. |
| `TestClient` (sync) | `AsyncClient` with `ASGITransport` | httpx 0.23+ | Async test client matches async app. Use httpx, not requests. |

## Open Questions

1. **Database path configuration**
   - What we know: `db/wise.db` is the planned path, config via pydantic-settings
   - What's unclear: Whether to use a single global connection or connection-per-request pattern
   - Recommendation: Start with connection-per-request via `get_db()`. Simpler, safer for concurrent access. Optimize later only if needed.

2. **Static file cache headers**
   - What we know: StaticFiles sets reasonable defaults
   - What's unclear: Whether dev mode needs cache-busting for CSS/JS iteration
   - Recommendation: Use `reload=True` in uvicorn for dev. No custom cache headers needed for local demo.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | None -- Wave 0 gap |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FRNT-03 (health) | Health check returns 200 with JSON | integration | `python -m pytest tests/test_health.py -x` | Wave 0 |
| FRNT-03 (db) | SQLite initializes with properties and assets tables | unit | `python -m pytest tests/test_database.py -x` | Wave 0 |
| FRNT-03 (static) | Root URL serves HTML page with 200 | integration | `python -m pytest tests/test_health.py::test_root_serves_html -x` | Wave 0 |
| FRNT-03 (css) | CSS file accessible at /css/styles.css | integration | `python -m pytest tests/test_health.py::test_css_accessible -x` | Wave 0 |
| FRNT-03 (wal) | WAL mode enabled on database connections | unit | `python -m pytest tests/test_database.py::test_wal_mode -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before verification

### Wave 0 Gaps
- [ ] `tests/__init__.py` -- package marker
- [ ] `tests/conftest.py` -- shared fixtures (async client, temp DB)
- [ ] `tests/test_health.py` -- health check + static file tests
- [ ] `tests/test_database.py` -- schema creation + WAL mode tests
- [ ] `pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` -- asyncio_mode = "auto"

## Sources

### Primary (HIGH confidence)
- [FastAPI Static Files docs](https://fastapi.tiangolo.com/tutorial/static-files/) -- StaticFiles mount, html=True parameter
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) -- lifespan context manager pattern
- [SQLite WAL documentation](https://sqlite.org/wal.html) -- WAL mode behavior and persistence
- [SQLite PRAGMA reference](https://sqlite.org/pragma.html) -- foreign_keys, journal_mode semantics
- [aiosqlite PyPI](https://pypi.org/project/aiosqlite/) -- v0.22.1, async SQLite wrapper

### Secondary (MEDIUM confidence)
- [Simon Willison WAL mode TIL](https://til.simonwillison.net/sqlite/enabling-wal-mode) -- WAL persistence behavior verified
- Project research: `.planning/research/STACK.md` -- version numbers, installation commands
- Project research: `.planning/research/ARCHITECTURE.md` -- project structure, patterns
- Project research: `.planning/research/PITFALLS.md` -- SQLite concurrency, StaticFiles ordering

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries pre-validated in project research, versions confirmed
- Architecture: HIGH -- project structure defined in architecture research, Phase 1 is a subset
- Pitfalls: HIGH -- StaticFiles mount order and WAL mode are well-documented behaviors

**Research date:** 2026-03-10
**Valid until:** 2026-04-10 (stable stack, no fast-moving dependencies)
