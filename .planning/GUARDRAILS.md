# 🚨 CRITICAL ARCHITECTURE GUARDRAILS

1. **Vector Dimension:** MUST hardcode outputDimensionality=3072.
2. **Task Types:** Files = RETRIEVAL_DOCUMENT, Queries = RETRIEVAL_QUERY.
3. **Signed URLs:** Direct browser-to-GCS only. Backend never touches bytes.
4. **No Conversions:** PDF (max 6p), Video (max 120s), Audio (max 80s) ONLY. Reject others.
5. **SQLite WAL:** Use "PRAGMA journal_mode=WAL;" for async concurrency.
6. **Strict JSON:** Enforce Gemini 2.5 Pro response_schema for all queries.
