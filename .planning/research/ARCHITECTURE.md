# Architecture Patterns

**Domain:** Multimodal property evaluation
**Researched:** 2026-03-10
**Confidence:** HIGH

## Recommended Architecture

Single-process Python application. FastAPI serves both API and static frontend. All AI calls go to Vertex AI. All file storage goes to GCS. Local persistence via SQLite + ChromaDB.

```
Browser (localhost:8000)
  |
  |-- Static files (HTML/CSS/JS) served by FastAPI StaticFiles
  |-- API calls to /api/* handled by FastAPI routes
  |-- File uploads go DIRECTLY to GCS (signed URL, bypasses FastAPI)
  |
FastAPI (thin router)
  |
  |-- SQLite (metadata: properties, assets)
  |-- ChromaDB (vectors: 3072-dim embeddings with metadata)
  |-- Vertex AI (Gemini Embedding 2 for vectors, Gemini 2.5 Pro for analysis)
  |-- GCS (file storage, signed URL generation)
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| FastAPI routes | HTTP routing, request validation, response serialization | All other components |
| SQLite via aiosqlite | Property + Asset metadata CRUD | FastAPI routes only |
| ChromaDB | Vector storage, cosine similarity search, property_id filtering | Embedding service, Query service |
| Embedding service | Takes gcs_uri, calls Gemini Embedding 2, stores vector in ChromaDB, updates SQLite | ChromaDB, SQLite, Vertex AI |
| Query service | Embeds question, searches ChromaDB, collects gs:// URIs, calls Gemini 2.5 Pro | ChromaDB, Vertex AI |
| GCS client | Generates signed URLs, deletes objects | FastAPI routes (upload-url, delete endpoints) |
| Frontend (static) | UI rendering, file drag-and-drop, polling, result display | FastAPI API via fetch() |

### Data Flow

**Ingest path:**
1. Browser requests signed URL from FastAPI (POST /api/properties/{id}/upload-url)
2. FastAPI creates Asset record in SQLite (embedded=false), generates signed URL
3. Browser PUTs file directly to GCS using signed URL (FastAPI never touches bytes)
4. Browser notifies FastAPI upload complete (POST /api/properties/{id}/assets/{asset_id}/embed)
5. FastAPI calls Gemini Embedding 2 with gs:// URI (taskType=RETRIEVAL_DOCUMENT, dims=3072)
6. Vector stored in ChromaDB with metadata {property_id, file_type, gcs_uri, filename}
7. Asset.embedded set to true in SQLite

**Query path:**
1. User submits question (POST /api/properties/{id}/query)
2. Question embedded via Gemini Embedding 2 (taskType=RETRIEVAL_QUERY, dims=3072)
3. ChromaDB cosine search with property_id filter, top-k=5
4. Matched gs:// URIs + question sent to Gemini 2.5 Pro with system prompt
5. Gemini 2.5 Pro returns structured JSON (forced via response_schema)
6. JSON returned to frontend for rendering

## Recommended Project Structure

```
vertex-property-evaluations/
  app/
    __init__.py
    main.py              # FastAPI app, lifespan, mount static files, include routers
    config.py             # GCP project, bucket name, model names, constants
    database.py           # SQLite schema, connection, aiosqlite helpers
    models.py             # Pydantic request/response models
    routers/
      __init__.py
      properties.py       # Property CRUD endpoints
      assets.py           # Upload URL, embed trigger, asset delete
      query.py            # Query endpoint
    services/
      __init__.py
      gcs.py              # Signed URL generation, file deletion
      embedding.py        # Gemini Embedding 2 wrapper + ChromaDB insert
      evaluation.py       # Gemini 2.5 Pro query + structured output
  static/
    index.html            # Property dashboard
    property.html         # Dossier view (two-pane)
    css/
      styles.css          # Dark theme styles
    js/
      api.js              # API client (fetch wrappers)
      upload.js           # Drop zone, file validation, signed URL flow
      polling.js          # Embedding status polling
      results.js          # Query results rendering
  data/
    chromadb/             # ChromaDB persistent storage (gitignored)
  db/
    wise.db               # SQLite database (gitignored)
  test-files/             # Test assets from risk spike
  gcp-credentials.json    # Service account key (gitignored)
  requirements.txt
  run.py                  # uvicorn launcher
```

### Structure Rationale

- **app/routers/:** Separate routers by domain keeps each file small. FastAPI `include_router` makes this clean.
- **app/services/:** Services encapsulate external dependencies (GCS, Gemini, ChromaDB). Routers never call SDKs directly -- they call services. Testable without HTTP.
- **static/:** Separate JS files per concern (upload, polling, results) prevent a single monolithic script. No build step needed.
- **data/ and db/:** Persistent local storage directories. Both gitignored, created on first run.

## Patterns to Follow

### Pattern 1: Thin Router / Fat Service

Route handlers validate input, call a service, return output. All logic lives in `app/services/`.

```python
# routers/assets.py -- thin
@router.post("/{property_id}/assets/{asset_id}/embed")
async def trigger_embed(property_id: str, asset_id: str):
    asset = await db.get_asset(asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    await embedding_service.embed_asset(asset)
    return {"status": "embedding"}

# services/embedding.py -- fat
async def embed_asset(asset: Asset):
    response = client.models.embed_content(
        model="gemini-embedding-2-preview",
        contents=[types.Part.from_uri(file_uri=asset.gcs_uri, mime_type=asset.mime_type)],
        config=types.EmbedContentConfig(
            output_dimensionality=3072,
            task_type="RETRIEVAL_DOCUMENT"
        )
    )
    vector = response.embeddings[0].values
    assert len(vector) == 3072
    await asyncio.to_thread(
        chroma_collection.upsert,
        ids=[asset.id],
        embeddings=[vector],
        metadatas=[{"property_id": asset.property_id, "file_type": asset.file_type,
                    "gcs_uri": asset.gcs_uri, "filename": asset.filename}]
    )
    await db.mark_embedded(asset.id)
```

### Pattern 2: Single GenAI Client Instance

Create one `genai.Client(vertexai=True, ...)` at app startup via FastAPI lifespan. Pass to services via app state.

```python
from contextlib import asynccontextmanager
from google import genai

@asynccontextmanager
async def lifespan(app):
    app.state.genai_client = genai.Client(
        vertexai=True,
        project="gen-lang-client-0138072717",
        location="us-central1"
    )
    yield

app = FastAPI(lifespan=lifespan)
```

### Pattern 3: Browser-Direct Upload (Signed URL Pattern)

```
Browser                    FastAPI                 GCS
  |                          |                       |
  |-- POST /upload-url ----->|                       |
  |                          |-- generate signed URL--|
  |<-- { signed_url } ------|                       |
  |                          |                       |
  |-- PUT file bytes -------------------------------->|
  |<-- 200 OK ----------------------------------------|
  |                          |                       |
  |-- POST /embed ---------->|                       |
  |                          |-- embed via Vertex AI--|
  |<-- { status } ----------|                       |
```

FastAPI never touches file bytes. Non-negotiable.

### Pattern 4: Property-Scoped Vector Search

Single ChromaDB collection (`property_assets`), filter by `property_id` in metadata on every query.

```python
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    where={"property_id": property_id}
)
```

### Pattern 5: Idempotent Embed Endpoint

If asset is already embedded, return success without re-embedding. Prevents wasting Vertex AI credits on retry.

## Anti-Patterns to Avoid

### Anti-Pattern 1: FastAPI as File Proxy
Receiving file bytes in FastAPI then forwarding to GCS. Blocks memory, freezes event loop on large videos.

### Anti-Pattern 2: Base64 Inline Embedding
Reading files from GCS into memory for embedding. Unnecessary -- Gemini accepts gs:// URIs natively.

### Anti-Pattern 3: Collection-Per-Property in ChromaDB
Creates file descriptor overhead. Metadata filtering on a single collection is the intended pattern.

### Anti-Pattern 4: Synchronous SQLite in Async Handlers
Using stdlib `sqlite3` directly blocks the event loop. Use `aiosqlite`.

### Anti-Pattern 5: LLM Orchestration Framework for 2 Calls
LangChain/LlamaIndex for 2 API calls (embed + analyze). 50+ transitive dependencies for zero benefit.

## Scalability Considerations

| Concern | Demo (3 properties) | Phase 2 (100 properties) | Production (10K properties) |
|---------|---------------------|--------------------------|----------------------------|
| Vector search | ChromaDB local, instant | ChromaDB local, still fast | Managed vector DB |
| File storage | GCS single bucket | GCS single bucket | GCS with lifecycle policies |
| Database | SQLite file | SQLite file | PostgreSQL |
| API auth | None | API key | OAuth2 / JWT |
| Concurrent users | 1 | 5-10 | Load balancer + workers |

**For MVP:** Every "Demo" column choice is correct. Do not build for Phase 2 scale during the MVP sprint.

## Sources

- Master spec (local: docs/superpowers/specs/2026-03-10-wise-evaluations-master-spec.md)
- Risk spike validation (local: risk_spike.py)
- [FastAPI StaticFiles docs](https://fastapi.tiangolo.com/tutorial/static-files/)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [ChromaDB usage guide](https://docs.trychroma.com/)
- [google-genai SDK docs](https://googleapis.github.io/python-genai/)
