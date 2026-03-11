# Wise Evaluations

## What This Is

A standalone multimodal property evaluation tool that lets real estate agents drop property media — photos, PDFs, video walkthroughs, and audio memos — into a single workspace and query across all of them for instant risk flags and valuation insights. Built as a 2-4 week MVP for a friendly sale demo to Wise Agent CRM.

## Core Value

Cross-modal risk discovery — connecting evidence across different media types (video, audio, photos, PDFs) that a human reviewer would miss, delivered as structured, actionable risk evaluations.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Direct-to-GCS file upload via signed URLs (browser never sends bytes to FastAPI)
- [ ] Multimodal embedding of all 4 media types (photo, PDF, video, audio) via Gemini Embedding 2
- [ ] Cross-modal vector search via ChromaDB with property-scoped filtering
- [ ] Structured risk evaluation via Gemini 2.5 Pro with enforced JSON schema
- [ ] Property CRUD (create, list, view, delete)
- [ ] Asset management (upload, embed, list, delete)
- [ ] Frontend with property dashboard, file drop zone, and query results panel
- [ ] Frontend file validation enforcing preview API limits
- [ ] Golden dossier with 3 pre-curated demo properties
- [ ] 5-minute demo flow including controlled live upload

### Out of Scope

- User authentication / multi-tenancy — solo demo, not production
- Team collaboration — not needed for MVP sale
- Production deployment — runs locally for demo
- DOCX support — Gemini preview API doesn't support it
- WebSockets — polling is sufficient for MVP
- CI/CD — solo dev, manual deployment
- Wise Agent CRM integration API — phase 2 after sale
- Arbitrary audience uploads during demo — controlled inputs only
- Document chunking for large files — preview API limits make this unnecessary

## Context

- **GCP Project:** `gen-lang-client-0138072717` (project number `934667728736`)
- **GCS Bucket:** `gs://wise-evaluations-media` in `us-central1`, CORS configured for localhost:8000
- **Credentials:** `gcp-credentials.json` (service account)
- **IAM:** Vertex AI service agent granted `roles/storage.objectViewer` on bucket
- **Billing:** Alerts at $50/$250/$500, $1,000 Vertex AI credit budget
- **Risk spike passed:** All 4 modalities + text query return 3072-dim vectors via `gs://` URIs
- **Venv ready:** `./venv/` with google-genai, google-cloud-storage, chromadb, opencv-python-headless
- **Master spec:** `docs/superpowers/specs/2026-03-10-wise-evaluations-master-spec.md`
- **Handoff:** `docs/superpowers/specs/2026-03-10-wise-evaluations-handoff.md`

## Constraints

- **API Limits:** PDF ≤6 pages, video ≤120s, audio ≤80s, images ≤20MB, no DOCX (Gemini preview API)
- **Budget:** $1,000 Vertex AI credits
- **Timeline:** 2-4 weeks to demo-ready MVP
- **Architecture:** FastAPI never touches file bytes — all uploads via signed URLs to GCS
- **Embeddings:** `outputDimensionality=3072` hardcoded on every call, `taskType` switching (RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY)
- **Output:** Gemini 2.5 Pro forced to structured JSON via `response_schema` — no free text parsing
- **Demo:** Controlled inputs only — no audience uploads

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ChromaDB over Pinecone/Weaviate | Local, file-based, no infra cost, sufficient for MVP | — Pending |
| SQLite over Postgres | Solo dev, local-only, zero ops | — Pending |
| No frontend framework (vanilla HTML/CSS/JS) | Speed of development, served by FastAPI StaticFiles | — Pending |
| Signed URL uploads (browser → GCS direct) | FastAPI never touches bytes, prevents UI freezing on large video | — Pending |
| Polling over WebSockets for embed status | Simple, no complexity, 2-second interval sufficient | — Pending |
| Dark theme UI | Professional demo aesthetic | — Pending |

---
*Last updated: 2026-03-10 after initialization*
