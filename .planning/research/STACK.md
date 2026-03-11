# Technology Stack

**Project:** Wise Evaluations
**Researched:** 2026-03-10
**Overall Confidence:** HIGH -- stack is already validated by risk spike; versions verified against PyPI/official sources

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| FastAPI | >=0.115.0 | API framework | Async-native, Pydantic v2 integration, built-in OpenAPI docs, StaticFiles for serving frontend. The only serious Python choice for async API work in 2026. | HIGH |
| Uvicorn | 0.41.0 | ASGI server | Already installed. Standard FastAPI companion. Use `uvicorn[standard]` for lifespan support. | HIGH |
| Python | 3.12+ | Runtime | Venv already active. 3.12 has the best balance of performance and library compatibility. | HIGH |

### AI / ML

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| google-genai | >=1.56.0 (venv has 1.66.0) | Gemini Embedding 2 + Gemini 2.5 Pro | The unified Google Gen AI SDK. Replaces both `google-generativeai` (dead Nov 2025) and `vertexai` generative modules (deprecated Jun 2025, removal Jun 2026). Already validated in risk spike. One SDK for both embedding and analysis. | HIGH |
| ChromaDB | 1.5.5 | Vector store | Already installed. Local, file-based, zero infra cost. Cosine distance, metadata filtering by property_id, persistent storage. Sufficient for MVP demo with <1000 vectors. No reason to bring in Pinecone/Weaviate for a local demo. | HIGH |

### Storage / Database

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| google-cloud-storage | 3.9.0 | GCS signed URLs + bucket ops | Already installed. Generates signed URLs for direct browser-to-GCS uploads. FastAPI never touches file bytes. | HIGH |
| SQLite (stdlib) | builtin | Relational metadata | Property + Asset tables. Zero ops, zero config, ships with Python. Solo dev, local-only demo -- Postgres is overkill. | HIGH |
| aiosqlite | 0.22.1 | Async SQLite access | Wraps stdlib sqlite3 for use in async FastAPI handlers without blocking the event loop. Critical for a framework that is async-native. | HIGH |

### Frontend

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Vanilla HTML/CSS/JS | N/A | UI | Served by FastAPI StaticFiles. No build step, no npm, no bundler. Two screens total. Adding React/Vue for 2 pages would be over-engineering for a 2-4 week MVP by a solo dev. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | 2.12.5 (installed) | Request/response validation, structured output schemas | Every endpoint -- FastAPI uses it natively. Also defines the Gemini 2.5 Pro response_schema. |
| pydantic-settings | 2.13.1 (installed) | Configuration management | Load GCP project ID, bucket name, credentials path from env vars or .env file. |
| python-multipart | latest | Form data parsing | FastAPI dependency for any form/file endpoints. Install even though we use signed URLs -- needed for form body parsing. |
| opencv-python-headless | 4.13.0.92 (installed) | Video duration extraction | Frontend validates video < 120s, but backend should double-check. cv2 reads duration without decoding full video. Headless = no GUI deps. |
| httpx | 0.28.1 (installed) | Async HTTP client | Used by FastAPI's test client. May also be useful for any GCS/Vertex AI interactions that need raw HTTP. |
| pytest | latest | Testing | Basic endpoint and pipeline tests. Not a test-heavy MVP, but sanity checks prevent demo embarrassment. |
| pytest-asyncio | latest | Async test support | FastAPI endpoints are async; tests need async fixtures. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| API Framework | FastAPI | Flask | Flask lacks native async, Pydantic integration, and auto-generated OpenAPI docs. No reason to use Flask for new async Python projects in 2026. |
| API Framework | FastAPI | Django | Massive overhead for a 7-endpoint API. Django ORM is wasted when using SQLite directly. |
| Vector Store | ChromaDB (local) | Pinecone | Cloud-hosted = network latency, API costs, account setup. MVP has <1000 vectors. Pinecone is for production scale. |
| Vector Store | ChromaDB (local) | Weaviate | Self-hosted Weaviate needs Docker. ChromaDB is pip install + 3 lines of code. |
| Vector Store | ChromaDB (local) | pgvector | Requires Postgres. We chose SQLite. Adding Postgres for vectors when ChromaDB works locally is unnecessary complexity. |
| Database | SQLite + aiosqlite | PostgreSQL | Postgres requires running a server. Solo dev, local demo, <100 rows of metadata. SQLite is the right tool. |
| Database | SQLite + aiosqlite | SQLAlchemy ORM | 2 tables, 5 columns each. An ORM adds abstraction without value. Raw SQL with aiosqlite is clearer and faster to write. |
| Frontend | Vanilla JS | React/Vue/Svelte | 2 screens, no complex state management, no component reuse. A framework adds a build pipeline and npm for zero benefit. |
| Frontend | Vanilla JS | HTMX | Tempting for polling, but the signed-URL upload flow needs JS anyway. Vanilla JS keeps it simple and dependency-free. |
| Google SDK | google-genai | vertexai (legacy) | vertexai generative modules deprecated Jun 2025, removal Jun 2026. google-genai is the unified replacement. Risk spike already validated it. |
| Google SDK | google-genai | google-generativeai | Dead since Nov 2025. Do not install. |

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| `google-generativeai` | End-of-life since November 2025. All support terminated. Use `google-genai` instead. |
| `vertexai` (generative modules) | Deprecated June 2025, scheduled removal June 2026. Migrating now avoids forced migration later. |
| LangChain | This project has exactly 2 LLM calls (embed + analyze). LangChain adds massive dependency bloat for chain/agent abstractions you do not need. Call the SDK directly. |
| LlamaIndex | Same reasoning as LangChain. The retrieval pipeline is 3 steps (embed query, search ChromaDB, pass to Gemini). LlamaIndex wraps this in abstractions that obscure what is happening. |
| SQLAlchemy | 2 tables. Raw SQL is faster to write, easier to debug, and has no migration framework to manage. |
| Docker (for MVP) | Local demo on one machine. Docker adds container build time to every iteration cycle. Ship without it. |
| Any CSS framework (Tailwind, Bootstrap) | Dark theme, 2 screens, custom layout. CSS custom properties + a few hundred lines of CSS. A framework adds build tooling or CDN dependency for marginal gain. |

## Installation

```bash
# From project root, with venv activated:

# Core framework (not yet installed)
pip install "fastapi[standard]" aiosqlite

# Already installed in venv (verify with pip list):
# google-genai, google-cloud-storage, chromadb, opencv-python-headless
# pydantic, pydantic-settings, uvicorn, httpx

# Dev dependencies
pip install pytest pytest-asyncio
```

**Note:** `fastapi[standard]` pulls in uvicorn, python-multipart, httpx, jinja2, and other useful defaults. Since uvicorn and httpx are already installed, pip will skip them.

## Version Pinning Strategy

For a 2-4 week MVP, pin loosely with `>=` minimums rather than exact versions. The venv is already set up and working. A `requirements.txt` with exact pins should be generated from `pip freeze` once the stack is fully installed, not maintained by hand.

```bash
# Generate after installing everything:
pip freeze > requirements.txt
```

## Architecture Implications

- **FastAPI + aiosqlite + google-genai** are all async-native. The entire request path from HTTP to database to Vertex AI is non-blocking.
- **ChromaDB** operations are synchronous but fast (local disk). For MVP scale, wrapping in `asyncio.to_thread()` is optional but recommended for the embed-then-store path.
- **StaticFiles** mount means single origin (`localhost:8000`) -- no CORS between frontend and API.
- **Signed URLs** mean FastAPI is a thin metadata router. It never buffers file bytes. This is critical for large video uploads.

## Sources

- [FastAPI PyPI](https://pypi.org/project/fastapi/) -- v0.135.x as of March 2026
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/)
- [ChromaDB PyPI](https://pypi.org/project/chromadb/) -- v1.5.5 as of March 2026
- [google-genai PyPI](https://pypi.org/project/google-genai/) -- v1.56.0+ (venv has 1.66.0)
- [google-genai GitHub](https://github.com/googleapis/python-genai)
- [Google Gen AI SDK Overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview) -- confirms vertexai deprecation
- [google-cloud-storage PyPI](https://pypi.org/project/google-cloud-storage/) -- v3.9.0 as of Feb 2026
- [Pydantic Changelog](https://docs.pydantic.dev/latest/changelog/) -- v2.12.5
- [Uvicorn PyPI](https://pypi.org/project/uvicorn/) -- v0.41.0
- [aiosqlite PyPI](https://pypi.org/project/aiosqlite/) -- v0.22.1
