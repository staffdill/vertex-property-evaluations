---
phase: 02-property-crud
plan: "02"
subsystem: api
tags: [fastapi, aiosqlite, gcs, chromadb, stubs]

# Dependency graph
requires:
  - phase: 02-01
    provides: properties router, assets table schema, AssetResponse model
provides:
  - Asset router stub at GET /api/properties/{id}/assets returning empty list
  - app/services/gcs.py stub with delete_prefix and generate_signed_url placeholders
  - app/services/embedding.py stub with delete_by_property and embed_asset placeholders
  - Established module paths for Phase 3 (GCS) and Phase 4 (embeddings)
affects: [03-file-upload, 04-embedding]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Stub modules with TODO comments gate future-phase implementations without blocking startup
    - Services directory as package under app/ for clean import paths

key-files:
  created:
    - app/routers/assets.py
    - app/services/__init__.py
    - app/services/gcs.py
    - app/services/embedding.py
  modified:
    - app/main.py

key-decisions:
  - "Stub services avoid importing chromadb and google-cloud-storage (not in venv) using TODO comments instead of import guards"
  - "Assets router uses same get_connection() pattern as properties router for PRAGMA foreign_keys=ON consistency"
  - "Assets router registered before StaticFiles mount in main.py to prevent route shadowing"

patterns-established:
  - "Stub pattern: async function with pass/return stub body + TODO PhaseN comment signals future implementation without breaking startup"
  - "Service layer under app/services/ separates business logic from routing"

requirements-completed: [PROP-03, PROP-04]

# Metrics
duration: 2min
completed: 2026-03-11
---

# Phase 2 Plan 02: Asset Router Stub and Service Placeholders Summary

**FastAPI asset router stub at GET /api/properties/{id}/assets with GCS and embedding service stubs establishing module paths for Phase 3 and Phase 4**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-11T18:58:28Z
- **Completed:** 2026-03-11T18:59:30Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Created `app/routers/assets.py` with stub GET endpoint querying the assets table (returns empty list, ready for Phase 3 POST/DELETE)
- Created `app/services/gcs.py` with `delete_prefix` and `generate_signed_url` stubs — no google-cloud-storage import at load time
- Created `app/services/embedding.py` with `delete_by_property` and `embed_asset` stubs — no chromadb import at load time
- Registered assets router in `app/main.py` before StaticFiles mount, all 17 tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Create asset router stub and service placeholder modules** - `fdae2c3` (feat)
2. **Task 2: Register assets router in main.py and verify full test suite** - `8b52030` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `app/routers/assets.py` - Stub GET /api/properties/{property_id}/assets endpoint
- `app/services/__init__.py` - Package marker for services directory
- `app/services/gcs.py` - GCS stub: delete_prefix, generate_signed_url (Phase 3 targets)
- `app/services/embedding.py` - Embedding stub: delete_by_property, embed_asset (Phase 4 targets)
- `app/main.py` - Added assets router import and include_router call

## Decisions Made
- Stub modules use TODO comments rather than TYPE_CHECKING guards since no type references to unavailable libraries were needed
- Assets router reuses the `get_connection()` generator pattern from properties.py to ensure PRAGMA consistency
- Module paths `app.services.gcs` and `app.services.embedding` are now importable for Phase 3 and Phase 4 without modifying main.py

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 (file upload): `app/services/gcs.py` ready for `google-cloud-storage` install and implementation
- Phase 4 (embedding): `app/services/embedding.py` ready for `chromadb` install and implementation
- Both routers registered, all tests green, server starts cleanly

---
*Phase: 02-property-crud*
*Completed: 2026-03-11*
