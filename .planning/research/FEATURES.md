# Feature Research

**Domain:** Multimodal property evaluation / real estate AI due diligence
**Researched:** 2026-03-10
**Confidence:** MEDIUM (emerging domain; competitor feature sets verified via web search, but cross-modal evaluation specifically is nascent -- few direct competitors exist)

## Feature Landscape

### Table Stakes (Users Expect These)

Features a buyer (Wise Agent CRM) or demo audience assumes exist. Missing these and the product feels broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Multi-file upload per property | Every property tool handles multiple files; single-file-at-a-time is a dealbreaker | MEDIUM | Drag-and-drop zone with progress indicators. Signed URL approach handles this cleanly. |
| Photo analysis with damage detection | Paraspot, Homesage, and insurance AI tools all do this. Baseline expectation for "AI property evaluation" | LOW (Gemini handles natively) | Gemini 2.5 Pro already detects cracks, stains, damage in images. No custom CV model needed. |
| PDF document extraction and risk flagging | V7 Go, Prophia, Kira.ai all extract clauses and flag risks from PDFs. Table stakes for due diligence. | LOW (Gemini handles natively) | Structured output schema already covers legal, financial, and compliance risk flags. |
| Structured risk report with severity levels | Every competitor (HouseCanary, SnapInspect, Paraspot) returns categorized findings with severity. Raw text output is unacceptable. | MEDIUM | Already designed: overall_risk_level, categorized risk_flags with severity dots. Critical for demo impact. |
| Property organization (CRUD) | Basic workspace management. Agents manage dozens of properties. | LOW | Property dashboard with cards, create/delete. Already spec'd. |
| Source attribution per finding | V7 Go's "AI Citations" feature (linking data points to source documents) sets the standard. Agents need to know WHY the AI flagged something. | MEDIUM | risk_flags already include source_files array. UI must render these as clickable references. |
| File type indicators and status | Users need to see what's uploaded, what type each file is, and whether it's been processed | LOW | File list with type icons and embedding status indicators (polling). Already spec'd. |
| Query input with natural language | HouseCanary CanaryAI and Fundrise RealAI both use conversational interfaces. Users expect to ask questions in plain English. | LOW | Text input + preset query chips already designed. |

### Differentiators (Competitive Advantage)

These are where Wise Evaluations competes. The core value proposition centers on cross-modal insight -- something no direct competitor currently delivers for individual property due diligence.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cross-modal insight discovery | THE differentiator. Connecting a ceiling stain in video, a verbal note in audio, and a clause in a PDF into one corroborated finding. No competitor does this for property due diligence today. HouseCanary works with data tables; Paraspot works with photos/video only; V7 Go works with documents only. None combine all four modalities. | HIGH (already solved architecturally) | Gemini Embedding 2 shared vector space + Gemini 2.5 Pro analysis makes this possible. The "wow moment" in the demo script. |
| Audio memo analysis | Inspectors record verbal observations during walkthroughs. No competitor ingests and cross-references audio memos with other media. Paraspot transcribes audio but doesn't cross-reference with documents. | LOW (Gemini handles natively) | Inspector audio is high-value, low-effort content that agents already create but can't search today. |
| Video walkthrough analysis | AI watches walkthrough video and identifies issues at specific timestamps. Paraspot does basic video analysis but doesn't cross-reference with PDF reports. | LOW (Gemini handles natively) | Timestamp-correlated findings ("water stain at 0:45") are viscerally impressive in demos. |
| Unified vector search across all modalities | Ask one question, get relevant evidence from photos, PDFs, video, and audio simultaneously. No need to search each file type separately. | HIGH (already solved) | ChromaDB cosine similarity across shared 3072-dim vector space. Property-scoped filtering prevents cross-contamination. |
| Real-time pipeline demonstration | Drop a file during the demo, watch it embed live, re-query to see updated results. Proves the system is real, not a slideshow. | MEDIUM | The "controlled live upload" in minute 5 of the demo script. Powerful for building buyer trust. |
| Pre-loaded golden dossiers | Demo opens with 3 curated properties (green/yellow/red risk). Immediate "this is real" impression. No competitor demo starts with pre-loaded realistic data. | MEDIUM | Requires sourcing/creating realistic demo files. The content quality IS the demo quality. |
| Preset query chips | "Risk assessment", "Valuation estimate", "Negotiation leverage", "Red flags summary" -- domain-specific shortcuts that show the product understands real estate workflows. | LOW | Already spec'd. Reduces friction for agents who don't know what to ask. |
| Valuation context (comp alignment, factors) | Goes beyond risk into valuation territory. HouseCanary does this with structured data; Wise Evaluations does it from unstructured media -- a different angle. | LOW (prompt engineering) | valuation_notes in structured output schema. Agents care deeply about pricing. |
| Risk badge on property cards | Green/yellow/red at-a-glance risk indicator on dashboard. Visual storytelling before you even open a property. | LOW | Derived from most recent query's overall_risk_level. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Automated property valuation (AVM) | HouseCanary's core product; buyers expect "the number" | Requires MLS data feeds, comp databases, and statistical models that are a separate product entirely. Wise Evaluations works with unstructured media, not structured market data. Building an AVM is a multi-year, data-intensive effort. | Provide qualitative valuation_notes from document analysis ("comps suggest below-market pricing based on inspection report findings") rather than a dollar figure. |
| Real-time collaboration / multi-user | Enterprise tools have it; seems like a natural next step | Adds auth, permissions, conflict resolution, WebSockets. Massive scope expansion for zero demo value. | Single-user MVP. Collaboration is a Phase 2 feature after the sale closes. |
| MLS integration / property data import | Wise Agent CRM already integrates with MLS. Seems natural. | Requires MLS API access (RETS/RESO), data licensing agreements, and market-specific configuration. Months of work for an MVP demo. | Manual property creation with name/address. CRM integration is Phase 2 after the sale. |
| Automated report PDF generation | Professional-looking PDF exports of risk evaluations | PDF generation libraries (ReportLab, WeasyPrint) add significant complexity. Layout, branding, pagination are time sinks. | On-screen structured results with clean formatting. PDF export is a Phase 2 feature. |
| Historical property tracking / trend analysis | Fundrise RealAI and HouseCanary offer trend data | Requires longitudinal data collection, time-series storage, and analytics infrastructure. No value for a demo with 3 pre-curated properties. | Each evaluation is a point-in-time snapshot. Trend analysis is a post-sale feature. |
| Custom AI model training on agent's data | "Can it learn my preferences?" | Fine-tuning requires training data pipelines, model hosting, evaluation infrastructure. Massive overkill for MVP. | Gemini 2.5 Pro with strong system prompts covers the use case. Prompt refinement is cheaper than fine-tuning. |
| DOCX support | Word documents are common in real estate | Gemini preview API explicitly does not support DOCX. Would require a conversion pipeline (DOCX-to-PDF) adding complexity and a failure point. | Require PDF format. State "PDF only" in the UI. Add DOCX-to-PDF conversion as a Phase 2 feature if the API limitation persists. |
| In-browser file preview/viewer | Users want to see what they uploaded | Rendering PDFs, playing video in-browser adds significant frontend complexity. The demo audience sees file names, not file contents. | File list with type icons and names. The AI's analysis of the files is the value, not viewing the files themselves. |
| Audience file uploads during demo | "Can I try my own file?" | Unvetted files may exceed preview API limits (>6 page PDFs, >120s video) causing live failures. Demo credibility destroyed. | Controlled inputs only. Script a polite deflection: "Google's model is in preview, so we're constraining file sizes for today." |
| WebSocket real-time updates | Feels more "modern" than polling | Connection lifecycle management, reconnection logic, error handling. Massive complexity for marginal UX improvement over 2-second polling. | Poll GET /api/properties/{id} on 2-second interval. Simple, reliable, sufficient. |
| Document chunking | "What about large PDFs?" | Preview API limits files to small sizes (6-page PDF, 120s video). Entire files fit in one embedding call. Chunking adds retrieval complexity (overlap, context windows). | Embed whole files. Chunking is a Phase 2 problem if/when API limits lift. |

## Feature Dependencies

```
Property CRUD
    |
    +--requires--> GCS Bucket + Signed URLs
    |                  |
    |                  +--requires--> CORS Configuration
    |                  +--requires--> IAM Permissions
    |
    +--enables--> Asset Upload (drag-and-drop)
                      |
                      +--requires--> Frontend File Validation (size/duration limits)
                      +--requires--> Signed URL Endpoint
                      |
                      +--enables--> Embedding Pipeline
                                        |
                                        +--requires--> Gemini Embedding 2 API access
                                        +--requires--> ChromaDB with 3072-dim vectors
                                        |
                                        +--enables--> Cross-Modal Query
                                                          |
                                                          +--requires--> Embedding Pipeline (for query embedding)
                                                          +--requires--> ChromaDB search
                                                          |
                                                          +--enables--> Structured Risk Evaluation
                                                                            |
                                                                            +--requires--> Gemini 2.5 Pro
                                                                            +--requires--> JSON response schema
                                                                            |
                                                                            +--enables--> Results UI (risk badges, flags, cross-modal insights)

Preset Query Chips --enhances--> Cross-Modal Query (reduces friction, no dependency)

Source Attribution --enhances--> Structured Risk Evaluation (rendered from source_files array)

Golden Dossier --requires--> Full pipeline working end-to-end
               --enables--> Demo rehearsal
```

### Dependency Notes

- **Asset Upload requires Property CRUD:** Files belong to properties. Property must exist before upload.
- **Embedding Pipeline requires Asset Upload:** Can only embed files that are in GCS.
- **Cross-Modal Query requires Embedding Pipeline:** ChromaDB must have vectors to search.
- **Structured Risk Evaluation requires Cross-Modal Query:** Gemini 2.5 Pro needs retrieved files as context.
- **Golden Dossier requires full pipeline:** All 3 demo properties need the complete ingest-to-query flow working.
- **Frontend File Validation prevents Embedding failures:** Catching oversized files before upload avoids API errors that would break the demo.

## MVP Definition

### Launch With (v1 -- Demo MVP)

- [ ] Property CRUD (create, list, view, delete) -- workspace foundation
- [ ] Direct-to-GCS file upload via signed URLs -- core ingest path
- [ ] Frontend file validation (size/duration limits) -- prevents API failures
- [ ] Multimodal embedding pipeline (photo, PDF, video, audio) -- the technical moat
- [ ] Cross-modal vector search with property scoping -- enables the "wow moment"
- [ ] Structured risk evaluation via Gemini 2.5 Pro -- the output users see
- [ ] Results UI with risk badges, categorized flags, source attribution -- demo polish
- [ ] Preset query chips -- reduces demo friction
- [ ] Cross-modal insights rendering -- THE differentiator on screen
- [ ] Golden dossier with 3 pre-curated properties -- controlled demo content
- [ ] 5-minute demo flow with controlled live upload -- the sales pitch

### Add After Validation (v1.x -- Post-Sale)

- [ ] Wise Agent CRM integration API -- trigger: sale closes, need to embed in their product
- [ ] Multi-user auth and property ownership -- trigger: CRM integration requires user scoping
- [ ] PDF report export -- trigger: agents ask "can I share this with my client?"
- [ ] DOCX-to-PDF conversion pipeline -- trigger: agents complain about PDF-only requirement
- [ ] Batch file upload with queue management -- trigger: agents uploading 20+ files per property
- [ ] In-browser file preview for uploaded assets -- trigger: repeated user requests

### Future Consideration (v2+)

- [ ] MLS data integration for automated comp analysis -- requires data licensing
- [ ] Historical evaluation tracking and trend analysis -- requires longitudinal data
- [ ] Mobile app for on-site inspection capture -- significant new platform
- [ ] Custom prompt templates per agent workflow -- requires user preference storage
- [ ] Webhook notifications for embedding completion -- replaces polling
- [ ] Predictive maintenance recommendations (Paraspot-style) -- requires historical property data

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Cross-modal insight discovery | HIGH | HIGH (solved) | P1 |
| Structured risk evaluation | HIGH | MEDIUM | P1 |
| Multi-file upload with drag-and-drop | HIGH | MEDIUM | P1 |
| Property CRUD | MEDIUM | LOW | P1 |
| Frontend file validation | HIGH | LOW | P1 |
| Source attribution per finding | HIGH | LOW | P1 |
| Audio memo analysis | HIGH | LOW | P1 |
| Video walkthrough analysis | HIGH | LOW | P1 |
| Golden dossier (demo data) | HIGH | MEDIUM | P1 |
| Risk badges (color-coded) | MEDIUM | LOW | P1 |
| Preset query chips | MEDIUM | LOW | P1 |
| Valuation context notes | MEDIUM | LOW | P2 |
| PDF report export | MEDIUM | MEDIUM | P3 |
| CRM integration API | HIGH | HIGH | P3 (post-sale) |
| MLS integration | HIGH | HIGH | P3 (post-sale) |

**Priority key:**
- P1: Must have for demo launch
- P2: Should have, add if time permits in Week 3-4
- P3: Post-sale features, not for MVP

## Competitor Feature Analysis

| Feature | HouseCanary CanaryAI | Paraspot AI | V7 Go (Lease Abstraction) | Wise Evaluations (Our Approach) |
|---------|---------------------|-------------|---------------------------|-------------------------------|
| Photo analysis | No (data-focused) | Yes (damage detection, room categorization) | No (document-focused) | Yes (Gemini 2.5 Pro) |
| Video analysis | No | Yes (walkthrough scanning) | No | Yes (Gemini 2.5 Pro) |
| Audio analysis | No | Transcription only | No | Yes (cross-referenced with all media) |
| PDF/document analysis | No | No | Yes (99% accuracy extraction) | Yes (Gemini 2.5 Pro) |
| Cross-modal correlation | **No** | **No** | **No** | **YES -- unique differentiator** |
| Structured risk output | Market data reports | Inspection reports | Lease abstracts | Risk evaluations with severity |
| Property valuation | AVM with 3% median error | No | No | Qualitative from documents |
| MLS integration | Deep (136M+ properties) | No | No | No (Phase 2) |
| CRM integration | API available | PMS integrations (AppFolio, Entrata, RealPage) | Enterprise API | Wise Agent CRM (Phase 2) |
| Pricing model | $69/mo+ | Per-inspection | Enterprise | License/white-label (TBD) |

**Key competitive insight:** No existing tool combines all four modalities (photo, video, audio, PDF) with cross-modal correlation for property due diligence. HouseCanary dominates structured data analysis. Paraspot dominates visual inspection. V7 Go dominates document extraction. Wise Evaluations occupies the unoccupied intersection -- and this gap is the entire sales pitch.

## Sources

- [HouseCanary CanaryAI](https://www.housecanary.com/products/canary-ai) -- generative AI for valuation and forecasting (136M+ properties, 3% median error)
- [Paraspot AI](https://www.paraspot.ai/) -- remote AI-powered property inspections with video/photo damage detection
- [V7 Labs - AI Tools for Real Estate 2026](https://www.v7labs.com/blog/best-ai-tools-for-real-estate) -- comprehensive field guide
- [Fundrise RealAI](https://www.cnbc.com/2026/01/27/new-ai-tool-from-fundrise-brings-high-level-cre-analysis-to-the-public.html) -- public CRE analysis tool
- [SnapInspect - AI Property Inspection](https://blog.snapinspect.com/how-ai-is-revolutionizing-property-inspection-software/) -- inspection software landscape
- [PropertyInspection.ai](https://propertyinspection.ai/) -- modular agentic AI for property
- [Homesage.ai - Property Evaluation APIs](https://homesage.ai/best-property-evaluation-apis-2026/) -- API comparison
- [Wise Agent CRM Features](https://wiseagent.com/features.asp) -- target CRM platform capabilities
- [Drooms - RE Due Diligence in the Age of AI](https://drooms.com/blog/real-estate/real-estate-due-diligence-in-the-age-of-ai/) -- due diligence AI landscape
- [GrowthFactor - AI Property Analysis Guide](https://www.growthfactor.ai/blog-posts/ai-property-analysis) -- platform comparison 2026

---
*Feature research for: Multimodal property evaluation / real estate AI due diligence*
*Researched: 2026-03-10*
