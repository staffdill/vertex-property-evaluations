# Requirements: Wise Evaluations

**Defined:** 2026-03-10
**Core Value:** Cross-modal risk discovery -- connecting evidence across different media types that a human reviewer would miss, delivered as structured, actionable risk evaluations.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Property Management

- [ ] **PROP-01**: User can create a property dossier with name and address
- [ ] **PROP-02**: User can view a list of all properties with file counts and risk badges
- [ ] **PROP-03**: User can view property details with all associated assets
- [ ] **PROP-04**: User can delete a property, cascading removal from SQLite, ChromaDB, and GCS

### File Upload

- [ ] **UPLD-01**: User can upload files directly from browser to GCS via signed URLs (FastAPI never touches bytes)
- [ ] **UPLD-02**: User can upload photos (JPEG, PNG, WebP, BMP, GIF), PDFs, videos (MP4, MOV, WebM, AVI), and audio (MP3, M4A, WAV, OGG)
- [ ] **UPLD-03**: Frontend blocks uploads exceeding preview API limits (PDF >6 pages, video >120s, audio >80s, images >20MB)
- [ ] **UPLD-04**: User can see embedding status for each asset (polling at 2-second intervals)
- [ ] **UPLD-05**: User can delete individual assets from a property

### Embedding Pipeline

- [ ] **EMBD-01**: System embeds uploaded assets via Gemini Embedding 2 using gs:// URIs with taskType=RETRIEVAL_DOCUMENT
- [ ] **EMBD-02**: All embedding calls hardcode outputDimensionality=3072 via a single wrapper function
- [ ] **EMBD-03**: Embedded vectors stored in ChromaDB with property_id, file_type, gcs_uri, and filename metadata

### Query & Analysis

- [ ] **QURY-01**: User can ask a natural language question about a property's files
- [ ] **QURY-02**: Question is embedded with taskType=RETRIEVAL_QUERY and matched via ChromaDB cosine similarity (top-k=5, property-scoped)
- [ ] **QURY-03**: Matched files sent to Gemini 2.5 Pro which returns structured JSON with risk_flags, severity, source attribution
- [ ] **QURY-04**: System identifies cross-modal insights connecting evidence across different media types
- [ ] **QURY-05**: User can use preset query chips ("Risk assessment", "Valuation estimate", "Negotiation leverage", "Red flags summary")

### Frontend UI

- [ ] **FRNT-01**: Property dashboard displays grid of cards with name, file count, and color-coded risk badge
- [ ] **FRNT-02**: Property dossier view has two-pane layout: left (drop zone + file list), right (query input + results)
- [x] **FRNT-03**: Dark theme professional aesthetic served by FastAPI StaticFiles
- [ ] **FRNT-04**: Results panel renders risk flags with severity dots, source file attribution, and cross-modal insights section

### Demo & Golden Dossier

- [ ] **DEMO-01**: Property 1 "1847 Ridgeline Dr" curated with 6 files across 4 modalities producing HIGH RISK with cross-modal insights
- [ ] **DEMO-02**: Property 2 "520 Maple Court" curated as clean property producing LOW RISK
- [ ] **DEMO-03**: Property 3 "9102 Oak Valley Ln" curated with HOA restriction producing MEDIUM RISK
- [ ] **DEMO-04**: Pre-vetted Foundation_Repair_Quote.pdf available for controlled live upload during demo

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Authentication & Multi-tenancy

- **AUTH-01**: User authentication with login/password
- **AUTH-02**: Multi-tenant data isolation per agent account

### CRM Integration

- **CRM-01**: Wise Agent CRM API integration for property import
- **CRM-02**: Push evaluation results back to CRM contact record

### Advanced Analysis

- **ANAL-01**: Automated valuation model (AVM) with comp data
- **ANAL-02**: MLS data integration for market context
- **ANAL-03**: Document chunking for files exceeding preview API limits

### Export & Reporting

- **RPRT-01**: PDF export of evaluation results
- **RPRT-02**: Shareable evaluation link for client review

## Out of Scope

| Feature | Reason |
|---------|--------|
| DOCX support | Gemini preview API does not support DOCX. PDFs only. |
| WebSockets for real-time updates | Polling at 2s interval is sufficient for MVP |
| CI/CD pipeline | Solo dev, manual deployment |
| Production deployment | Runs locally for demo presentation |
| Arbitrary audience uploads | Controlled inputs only -- preview API limits break on unvetted files |
| Team collaboration | Not needed for MVP sale demonstration |
| Mobile-responsive UI | Desktop-only demo presentation |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROP-01 | Phase 2 | Pending |
| PROP-02 | Phase 2 | Pending |
| PROP-03 | Phase 2 | Pending |
| PROP-04 | Phase 2 | Pending |
| UPLD-01 | Phase 3 | Pending |
| UPLD-02 | Phase 3 | Pending |
| UPLD-03 | Phase 3 | Pending |
| UPLD-04 | Phase 3 | Pending |
| UPLD-05 | Phase 3 | Pending |
| EMBD-01 | Phase 4 | Pending |
| EMBD-02 | Phase 4 | Pending |
| EMBD-03 | Phase 4 | Pending |
| QURY-01 | Phase 5 | Pending |
| QURY-02 | Phase 5 | Pending |
| QURY-03 | Phase 5 | Pending |
| QURY-04 | Phase 6 | Pending |
| QURY-05 | Phase 6 | Pending |
| FRNT-01 | Phase 7 | Pending |
| FRNT-02 | Phase 8 | Pending |
| FRNT-03 | Phase 1 | Complete |
| FRNT-04 | Phase 8 | Pending |
| DEMO-01 | Phase 9 | Pending |
| DEMO-02 | Phase 9 | Pending |
| DEMO-03 | Phase 9 | Pending |
| DEMO-04 | Phase 9 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0

---
*Requirements defined: 2026-03-10*
*Last updated: 2026-03-10 after roadmap creation*
