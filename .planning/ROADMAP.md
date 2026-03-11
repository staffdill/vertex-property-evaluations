# Roadmap: Wise Evaluations

## Overview

Wise Evaluations delivers a multimodal property evaluation tool in 9 phases following the strict technical dependency chain: foundation, then property management, then file upload, then embedding, then query/analysis, then frontend polish, then demo preparation. Each phase delivers a verifiable capability that unblocks the next. The final phase produces a rehearsed 5-minute demo ready for the Wise Agent CRM friendly sale.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Project Foundation** - FastAPI skeleton, SQLite schema, project structure, dev server
- [ ] **Phase 2: Property CRUD** - Property create, list, view, delete with database persistence
- [ ] **Phase 3: File Upload Pipeline** - Signed URL upload to GCS, file validation, asset management
- [ ] **Phase 4: Embedding Pipeline** - Gemini Embedding 2 integration with ChromaDB vector storage
- [ ] **Phase 5: Query and Analysis** - Natural language query with vector search and Gemini 2.5 Pro structured evaluation
- [ ] **Phase 6: Cross-Modal Insights** - Cross-modal evidence correlation and preset query chips
- [ ] **Phase 7: Frontend Dashboard** - Property grid cards with risk badges, dark theme, static file serving
- [ ] **Phase 8: Frontend Dossier View** - Two-pane property view with drop zone, file list, query input, and results panel
- [ ] **Phase 9: Golden Dossier and Demo** - Three curated demo properties, controlled live upload, end-to-end demo flow

## Phase Details

### Phase 1: Project Foundation
**Goal**: A running FastAPI application with SQLite database, project structure, and dev server that serves as the skeleton for all subsequent phases
**Depends on**: Nothing (first phase)
**Requirements**: FRNT-03
**Success Criteria** (what must be TRUE):
  1. FastAPI dev server starts and responds to health check at localhost:8000
  2. SQLite database initializes with properties and assets tables on first run
  3. Static file serving works (a test HTML page renders at the root URL)
  4. Dark theme base CSS is in place and applies to the test page
**Plans**: 2 plans

Plans:
- [ ] 01-01-PLAN.md — FastAPI skeleton, SQLite schema, static files with dark theme, test infrastructure
- [ ] 01-02-PLAN.md — Gap closure: dependency check in run.py, stale artifact cleanup

### Phase 2: Property CRUD
**Goal**: Users can create, view, list, and delete property dossiers through working API endpoints
**Depends on**: Phase 1
**Requirements**: PROP-01, PROP-02, PROP-03, PROP-04
**Success Criteria** (what must be TRUE):
  1. User can create a property dossier by providing a name and address
  2. User can view a list of all properties showing name and address
  3. User can view a single property's detail page showing its metadata
  4. User can delete a property, removing it from the database
  5. Deleting a property cascades to remove associated assets from SQLite, ChromaDB, and GCS
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — TDD: Pydantic models, property CRUD router, 8 integration tests (PROP-01 through PROP-04)
- [ ] 02-02-PLAN.md — Asset router stub and service placeholder modules for Phase 3/4 hookup

### Phase 3: File Upload Pipeline
**Goal**: Users can upload property files directly from the browser to GCS via signed URLs, with frontend validation enforcing API limits
**Depends on**: Phase 2
**Requirements**: UPLD-01, UPLD-02, UPLD-03, UPLD-04, UPLD-05
**Success Criteria** (what must be TRUE):
  1. User can upload photos, PDFs, videos, and audio files through a browser drop zone that sends bytes directly to GCS (not through FastAPI)
  2. Frontend blocks uploads that exceed preview API limits before the upload starts (PDF >6 pages, video >120s, audio >80s, images >20MB)
  3. User can see each asset's embedding status updating via polling at 2-second intervals
  4. User can delete individual assets from a property, removing them from SQLite and GCS
  5. Asset records are created in SQLite with correct file type, GCS URI, and property association
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD
- [ ] 03-03: TBD

### Phase 4: Embedding Pipeline
**Goal**: Uploaded assets are automatically embedded via Gemini Embedding 2 and stored in ChromaDB for vector search
**Depends on**: Phase 3
**Requirements**: EMBD-01, EMBD-02, EMBD-03
**Success Criteria** (what must be TRUE):
  1. After a file is uploaded, the system embeds it via Gemini Embedding 2 using the gs:// URI with taskType=RETRIEVAL_DOCUMENT
  2. All embedding calls use outputDimensionality=3072 through a single wrapper function (no scattered API calls)
  3. Embedded vectors are stored in ChromaDB with property_id, file_type, gcs_uri, and filename metadata
  4. Asset embedding status transitions from "pending" to "complete" (or "failed") and is visible via the polling endpoint
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

### Phase 5: Query and Analysis
**Goal**: Users can ask natural language questions about a property and receive structured risk evaluations from Gemini 2.5 Pro
**Depends on**: Phase 4
**Requirements**: QURY-01, QURY-02, QURY-03
**Success Criteria** (what must be TRUE):
  1. User can type a natural language question about a property's files and submit it
  2. The question is embedded with taskType=RETRIEVAL_QUERY and matched via ChromaDB cosine similarity (top-k=5, filtered to the current property)
  3. Matched files are sent to Gemini 2.5 Pro which returns structured JSON with risk_flags, severity, and source attribution
  4. The structured JSON response is validated against a Pydantic schema (no free-text parsing)
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

### Phase 6: Cross-Modal Insights
**Goal**: The analysis pipeline surfaces cross-modal connections and users can trigger common queries via preset chips
**Depends on**: Phase 5
**Requirements**: QURY-04, QURY-05
**Success Criteria** (what must be TRUE):
  1. Analysis results include a cross-modal insights section identifying connections between evidence from different media types (e.g., video damage + PDF repair quote)
  2. User can click preset query chips ("Risk assessment", "Valuation estimate", "Negotiation leverage", "Red flags summary") instead of typing
  3. Preset chips produce the same structured output format as free-text queries
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD

### Phase 7: Frontend Dashboard
**Goal**: A polished property dashboard with visual risk indicators that serves as the landing page
**Depends on**: Phase 2, Phase 5
**Requirements**: FRNT-01
**Success Criteria** (what must be TRUE):
  1. Property dashboard displays a grid of cards showing property name, file count, and color-coded risk badge (green/yellow/red)
  2. Risk badges reflect actual analysis results (not hardcoded values)
  3. Dashboard updates when properties are created or deleted
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

### Phase 8: Frontend Dossier View
**Goal**: A complete property workspace with file management and query results rendering
**Depends on**: Phase 3, Phase 6, Phase 7
**Requirements**: FRNT-02, FRNT-04
**Success Criteria** (what must be TRUE):
  1. Property dossier view has a two-pane layout: left pane with drop zone and file list, right pane with query input and results
  2. Drop zone accepts drag-and-drop and file picker for all supported media types
  3. Results panel renders risk flags with severity dots (color-coded), source file attribution (which file produced each flag), and a cross-modal insights section
  4. File list shows each asset with its type, name, and embedding status
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

### Phase 9: Golden Dossier and Demo
**Goal**: Three pre-curated demo properties are loaded and a rehearsed 5-minute demo flow works end-to-end
**Depends on**: Phase 8
**Requirements**: DEMO-01, DEMO-02, DEMO-03, DEMO-04
**Success Criteria** (what must be TRUE):
  1. "1847 Ridgeline Dr" is loaded with 6 files across 4 modalities and produces HIGH RISK with visible cross-modal insights when queried
  2. "520 Maple Court" is loaded as a clean property producing LOW RISK when queried
  3. "9102 Oak Valley Ln" is loaded with HOA restriction content producing MEDIUM RISK when queried
  4. A controlled live upload of Foundation_Repair_Quote.pdf during demo changes the risk assessment visibly
  5. The complete 5-minute demo flow (dashboard overview, dossier drill-down, live upload, query, results) works without errors
**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD
- [ ] 09-03: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Foundation | 0/1 | Not started | - |
| 2. Property CRUD | 0/2 | Not started | - |
| 3. File Upload Pipeline | 0/3 | Not started | - |
| 4. Embedding Pipeline | 0/2 | Not started | - |
| 5. Query and Analysis | 0/2 | Not started | - |
| 6. Cross-Modal Insights | 0/2 | Not started | - |
| 7. Frontend Dashboard | 0/1 | Not started | - |
| 8. Frontend Dossier View | 0/2 | Not started | - |
| 9. Golden Dossier and Demo | 0/3 | Not started | - |
