# Domain Pitfalls

**Domain:** Multimodal property evaluation with Gemini preview APIs
**Researched:** 2026-03-10
**Confidence:** HIGH

## Critical Pitfalls

Mistakes that cause rewrites, demo failures, or wasted days.

### Pitfall 1: ChromaDB Dimension Lock-In on First Insert

**What goes wrong:** ChromaDB locks collection dimensionality to the first vector inserted. If any embedding call omits `outputDimensionality=3072`, it returns a different-sized vector. ChromaDB rejects all subsequent inserts with `InvalidDimensionException`. The collection must be deleted and recreated, losing all data.

**Why it happens:** A single code path that forgets `outputDimensionality=3072`. Copy-paste errors, quick tests, or a refactored utility that drops the config.

**Consequences:** All embeddings fail. Full re-embed of all assets required.

**Prevention:** Create a single `get_embedding()` function that hardcodes dimensions. Never call `embed_content` directly from endpoint code. Assert `len(vector) == 3072` before every ChromaDB insertion.

**Detection:** `InvalidDimensionException` on ChromaDB insert. Multiple places calling `embed_content` directly.

### Pitfall 2: Gemini Structured Output Schema Rejection

**What goes wrong:** Gemini 2.5 Pro's structured output silently constrains JSON Schema features. Using `anyOf`, `dict[str, T]`, sets, or deeply nested optional objects causes `InvalidArgument: 400` at runtime. The SDK validator may reject schemas the API accepts (or vice versa).

**Why it happens:** Developers design the Pydantic schema assuming full JSON Schema support. The `risk_flags` array with nested objects and the `valuation_notes` nested object are the most likely offenders.

**Consequences:** Query endpoint returns 500. Demo shows error instead of results.

**Prevention:** Test the exact schema against the live API before building the results parser. Use `response_json_schema` (raw dict) instead of `response_schema` (Pydantic model) if SDK validation rejects a valid schema. Keep schema as flat as possible. Minimize `Optional` fields.

**Detection:** `InvalidArgument: 400` when calling Gemini with structured output.

### Pitfall 3: Forgetting taskType Switching

**What goes wrong:** Using `RETRIEVAL_DOCUMENT` for query text or `RETRIEVAL_QUERY` for files. Embeddings land in different vector space regions. Queries return irrelevant results.

**Why it happens:** Copy-paste from document embedding code. The API accepts both without error.

**Consequences:** Queries return wrong files. Demo produces nonsensical risk assessments.

**Prevention:** Constants: `TASK_TYPE_DOC = "RETRIEVAL_DOCUMENT"`, `TASK_TYPE_QUERY = "RETRIEVAL_QUERY"`. Single embedding function with explicit `task_type` parameter. Never default.

**Detection:** Query results consistently irrelevant despite correct files embedded.

### Pitfall 4: Gemini Hallucination in Cross-Modal Evaluation

**What goes wrong:** Gemini 2.5 Pro fabricates risk flags not present in source files, invents cross-modal correlations, or confidently states property values with no basis. Structured JSON makes hallucination harder to detect because output "looks right."

**Why it happens:** The model generates plausible risk flags even with insufficient evidence. Cross-modal insights are the core value but also where hallucination is most likely.

**Consequences:** Demo shows fabricated critical risks. Credibility destroyed.

**Prevention:** System prompt must instruct: "If you cannot identify specific evidence, do NOT include the risk flag. An empty array is better than fabricated flags." Validate `source_files` against actual property assets. Curate golden dossier files with known risks. Manually verify every output during rehearsal.

**Detection:** Risk flags citing nonexistent files. Cross-modal insights referencing vague timestamps. Confidence scores always above 0.8.

### Pitfall 5: Missing IAM Role = Silent Upload + Failed Embedding

**What goes wrong:** Files upload to GCS (signed URL works), but Gemini Embedding 2 returns 403 reading the gs:// URI.

**Why it happens:** Upload uses service account signing key. Embedding uses Vertex AI Service Agent. Different auth paths. The agent needs `roles/storage.objectViewer` on the bucket.

**Consequences:** User sees "upload complete" but embedding silently fails.

**Prevention:** Already configured in Day Zero (risk spike verified). If bucket or project changes, re-apply IAM. Log exact Vertex AI errors -- do not swallow them.

**Detection:** Embedding endpoint returns error. Check service agent permissions.

## Moderate Pitfalls

### Pitfall 6: SQLite Write Contention Under Concurrent Embeds

**What goes wrong:** User drops 6 files at once. 6 concurrent embed operations try to update SQLite simultaneously. `database is locked` errors. Embedding succeeds in Gemini/ChromaDB but status update fails, leaving assets stuck at `embedded: false`.

**Prevention:** Enable WAL mode: `PRAGMA journal_mode=WAL`. Set connection timeout to 30 seconds. Use aiosqlite (not sync sqlite3) for non-blocking access.

### Pitfall 7: Signed URL Expiry During Slow Upload

**What goes wrong:** Signed URL expires before large video upload completes.

**Prevention:** Set expiration to 15-30 minutes (not 5). 120s video at reasonable bitrate finishes in under 2 minutes.

### Pitfall 8: CORS Cache Poisoning After Config Change

**What goes wrong:** After updating GCS CORS config, browsers cache old preflight responses. CORS errors appear random.

**Prevention:** `maxAgeSeconds: 3600` means changes take up to 1 hour. Test in incognito after CORS changes.

### Pitfall 9: ChromaDB Collection Not Found After Restart

**What goes wrong:** App restarts, ChromaDB cannot find collection.

**Prevention:** Use persistent client with explicit path (`./data/chromadb/`). Use `get_or_create_collection()` not `create_collection()`.

### Pitfall 10: GCS Object Orphans on Property Delete

**What goes wrong:** Deleting property removes SQLite and ChromaDB records but leaves files in GCS. Orphaned files accumulate.

**Prevention:** Delete in order: (1) ChromaDB vectors, (2) GCS objects by prefix `{property_id}/`, (3) SQLite records. If GCS delete fails, metadata intact for retry.

## Minor Pitfalls

### Pitfall 11: Content-Type Mismatch on Signed URL PUT

Browser must set Content-Type header matching signed URL's content_type parameter exactly.

### Pitfall 12: Garbage Embeddings Pass Silently

Blurry photos, silent audio, scanned PDFs produce valid 3072-dim vectors that pollute search results. For demo, curate high-quality files. Consider filtering ChromaDB results below cosine similarity threshold of 0.3.

### Pitfall 13: Demo Data Quality IS Demo Quality

Generic stock photos and blank PDFs produce weak cross-modal insights. Invest real time creating compelling golden dossier files with visible defects, specific verbal concerns, and flaggable contract clauses.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| FastAPI skeleton (Week 1) | Sync SQLite in async handlers | Use aiosqlite from day one. Enable WAL mode. |
| Signed URL upload (Week 1) | CORS or Content-Type mismatch | Test with real browser upload, not just curl. |
| Embedding pipeline (Week 2) | Dimension mismatch or taskType error | Single embedding function. Assert vector length. |
| Query pipeline (Week 2) | Gemini rejects structured output schema | Test exact schema against live API first. |
| Frontend drop zone (Week 2) | File validation bypassed | Validate duration/pages/size in JS before upload. |
| Golden dossier (Week 3) | Weak demo data | Start sourcing files early. Quality > quantity. |
| Demo rehearsal (Week 4) | Live upload file fails | Test exact file 10 times. Have backup pre-embedded version. |

## "Looks Done But Isn't" Checklist

- [ ] Signed URL upload succeeds but file is 0 bytes in GCS (Content-Length not set)
- [ ] Vector in ChromaDB but `Asset.embedded` still false (SQLite lock during update)
- [ ] Gemini returns valid JSON but `source_files` references non-existent assets
- [ ] Property deleted from SQLite but GCS objects and ChromaDB vectors remain
- [ ] Frontend validates image size and video duration but not PDF page count
- [ ] CORS works for `localhost:8000` but breaks for `127.0.0.1:8000`
- [ ] Golden dossier embedded with different dimensionality during testing
- [ ] Schema validates locally with Pydantic but Gemini API rejects at runtime

## Sources

- Risk spike results (local: risk_spike.py)
- Master spec guardrails (local: docs/superpowers/specs/2026-03-10-wise-evaluations-master-spec.md)
- [ChromaDB FAQ](https://cookbook.chromadb.dev/faq/)
- [GCS signed URL docs](https://cloud.google.com/storage/docs/access-control/signed-urls)
- [Gemini structured output docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output)
- [google-genai GitHub issues](https://github.com/googleapis/python-genai/issues)
