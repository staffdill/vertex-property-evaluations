# Research Summary: Wise Evaluations

**Domain:** Multimodal property evaluation / real estate AI due diligence
**Researched:** 2026-03-10
**Overall Confidence:** HIGH

## Executive Summary

Wise Evaluations occupies a genuine market gap. Existing tools specialize in one modality -- HouseCanary does structured market data, Paraspot does visual inspection from photos/video, V7 Go does document extraction. No competitor combines all four modalities (photo, video, audio, PDF) with cross-modal correlation for property due diligence. This is the entire sales pitch.

The stack is validated and ready to build. The risk spike confirmed Gemini Embedding 2 embeds all four modalities into a shared 3072-dim vector space via gs:// URIs. The venv has all core dependencies installed (google-genai 1.66.0, ChromaDB 1.5.5, google-cloud-storage 3.9.0, Pydantic 2.12.5, uvicorn 0.41.0). Only FastAPI and aiosqlite need to be installed. The architecture is deliberately simple: single-process FastAPI serving both API and static frontend, SQLite for metadata, ChromaDB for vectors, GCS for file bytes.

The biggest risks are not technical but experiential: Gemini hallucination in cross-modal evaluation (fabricating risk flags), structured output schema rejection by the preview API, and golden dossier quality determining demo quality. All three are mitigated by early testing against the live API and careful demo data curation.

The project is correctly scoped for a 2-4 week solo dev sprint. Every "Phase 2" feature (auth, CRM integration, PDF export, MLS data) has been explicitly deferred. The stack choices (SQLite over Postgres, ChromaDB over Pinecone, vanilla JS over React) are right for the scope and timeline.

## Key Findings

**Stack:** FastAPI + aiosqlite + google-genai (unified SDK) + ChromaDB + GCS + vanilla JS. All current versions verified. Only `pip install "fastapi[standard]" aiosqlite` needed beyond existing venv.

**Architecture:** Single-process app. FastAPI as thin router. Signed URLs for browser-direct-to-GCS uploads (FastAPI never touches file bytes). One ChromaDB collection with property_id metadata filtering. Two Vertex AI calls: embed (Gemini Embedding 2) and analyze (Gemini 2.5 Pro with structured output).

**Critical pitfall:** Gemini 2.5 Pro hallucination in cross-modal evaluation. Structured JSON output makes hallucinated "critical" risk flags look authoritative. Mitigation: curated demo data + prompt engineering + manual verification during rehearsal.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Foundation (Week 1)** - FastAPI skeleton, SQLite schema, GCS signed URL endpoint, Property CRUD
   - Addresses: Project structure, database setup, core upload flow
   - Avoids: SQLite write contention (enable WAL mode from day one)

2. **Pipeline (Week 2)** - Embedding pipeline, query pipeline, basic frontend
   - Addresses: The core technical value (embed + search + analyze)
   - Avoids: Structured output schema rejection (test schema against live API first)

3. **UI + Demo Polish (Week 3)** - Results panel, risk badges, cross-modal insights rendering, golden dossier
   - Addresses: Demo-readiness, visual impact
   - Avoids: Weak demo data (start sourcing golden dossier files early)

4. **Buffer + Rehearsal (Week 4)** - Prompt tuning, edge case fixes, demo rehearsal
   - Addresses: Production quality for demo
   - Avoids: Gemini hallucination (manually verify every output)

**Phase ordering rationale:**
- Strict technical dependency chain: CRUD -> Upload -> Embed -> Query -> Frontend -> Demo data
- Each phase validates the next: signed URLs prove GCS integration before embedding depends on it
- Golden dossier creation should start in Week 2 (sourcing files) even though it ships in Week 3
- Week 4 buffer is essential -- prompt tuning with real data always takes longer than expected

**Research flags for phases:**
- Phase 2 (Pipeline): Needs validation that Gemini 2.5 Pro accepts the exact structured output schema. Test before building the results parser.
- Phase 3 (Demo Polish): Needs careful attention to demo data quality. Cross-modal insights are only as good as the curated files.
- Phase 4 (Rehearsal): Standard patterns, but prompt tuning may require multiple iterations.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI. Venv already has most deps. google-genai is the correct unified SDK (vertexai deprecated, google-generativeai dead). |
| Features | MEDIUM | Cross-modal evaluation is a genuine market gap (no competitor does it), but the domain is emerging. Competitor feature sets verified via web search. |
| Architecture | HIGH | Validated by risk spike. Signed URL pattern, gs:// URI embedding, ChromaDB metadata filtering all confirmed working. |
| Pitfalls | HIGH | Critical pitfalls (dimension lock-in, IAM roles, taskType switching) directly from risk spike experience. Gemini hallucination risk well-documented. |

## Gaps to Address

- **Structured output schema validation:** Must test the exact Pydantic schema against Gemini 2.5 Pro live API before building the results parser. This is the highest-risk unknown.
- **PDF page count validation in frontend:** No simple browser-side way to count PDF pages. May need to accept the API error and surface it clearly, or use pdf.js for page counting.
- **Golden dossier file sourcing:** Need to find/create realistic property inspection files (video with visible damage, audio with inspector verbal notes, PDFs with flaggable clauses). Quality of these files determines demo success.
- **Gemini Embedding 2 GA timeline:** Currently preview. If API behavior or limits change mid-sprint, the pipeline may need adjustment. Monitor release notes.
