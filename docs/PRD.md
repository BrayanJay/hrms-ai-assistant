# Product Requirements Document
# Astrynox AI — Enterprise Internal Knowledge Assistant

**Version:** 1.0  
**Methodology:** Agile Scrum  
**Sprint Duration:** 1 week  
**MVP Duration:** 4 Sprints (4 weeks)  
**Document Status:** Active  

---

## 1. Project Overview

**Astrynox AI** is an enterprise internal knowledge assistant that allows employees to query company documents, policies, memos, and website content through a conversational interface. It uses a Hybrid Multimodal RAG (Retrieval-Augmented Generation) pipeline to retrieve and reason over text, tables, images, and charts — returning accurate answers with inline citations including visual assets.

---

## 2. Problem Statement

Employees waste time searching through scattered company documents, policy files, and internal resources. Key information is buried in PDFs, PPTX decks, and web pages that are difficult to search effectively. Astrynox AI centralizes this knowledge and makes it instantly queryable through natural language.

---

## 3. Goals & Objectives

| Goal | Metric |
|------|--------|
| Reduce time employees spend searching documents | Answer returned in < 5 seconds |
| Provide accurate, cited answers | Citations attached to every answer |
| Support multimodal documents | Handle text, tables, images, charts |
| Controlled document ingestion | Admin-only upload with audit trail |
| Secure access | Email login with OTP verification, Google OAuth2 login |

---

## 4. Target Users

### Persona 1 — Employee (End User)
- Queries the system via chat interface
- Reads answers with cited sources
- Cannot upload or manage documents
- Expects fast, accurate, reliable answers

### Persona 2 — Admin
- Uploads and manages company documents
- Triggers web scraping for company website
- Manages user access
- Monitors ingestion status and errors

---

## 5. Scope

### In Scope (MVP — Phase 1)
- Document ingestion: PDF, DOCX, PPTX, HTML, scanned documents (OCR), XLSX/CSV
- Company website scraping for common Q&A content
- Hybrid RAG pipeline (dense + sparse retrieval, RRF fusion)
- Multimodal processing (VLM for images/charts, LLM for long text, table extraction)
- Hierarchical chunking with parent-child tree
- Qdrant vector database storage
- Redis 2-layer cache (Answer Cache + Embedding Cache)
- Relevance threshold check before LLM call
- Citations — text, image, table, chart
- Web app chat interface (Next.js)
- Admin dashboard for document management
- Authentication — email/password with OTP via Resend + Google OAuth2 (no OTP)
- REST API
- English language only
- Local deployment (MVP), AWS-ready architecture

### Out of Scope (Phase 2)
- Multilingual support (Sinhala, Tamil)
- Cross-encoder reranker
- Query rewriting / HyDE
- L3 Retrieval Cache (embedding vector key)
- Conversation memory / multi-turn context
- Analytics dashboard
- Role-based access beyond Admin/Employee
- Mobile application

---

## 6. Technical Architecture

### 6.1 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend Framework | Next.js (React, App Router) |
| Frontend Styling | Tailwind CSS + shadcn/ui |
| Frontend State | TanStack Query (server state) |
| Backend API | Python — FastAPI |
| Relational DB | PostgreSQL |
| LLM / VLM | OpenAI GPT-4o |
| Embeddings (Dense) | BAAI/bge-large-en-v1.5 (local, via sentence-transformers) |
| Embeddings (Sparse) | BM25 (rank-bm25) |
| Vector Database | Qdrant (single collection, all modalities) |
| Cache | Redis (2-layer: Answer Cache + Embedding Cache) |
| Document Parser | Docling |
| OCR | Tesseract (MVP) |
| Image Optimization | Pillow (resize → WebP → base64) |
| Web Scraping | BeautifulSoup + Playwright |
| Authentication | JWT + Google OAuth2 + Resend OTP (email only) |
| Asset Storage | Qdrant payload as base64 (MVP) → AWS S3 (production) |
| Containerization | Docker + Docker Compose |
| Deployment (MVP) | Localhost |
| Deployment (Prod) | AWS (ECS / EC2) |

---

### 6.2 Ingestion Pipeline (Phase 1)

```
Raw File (PDF, DOCX, PPTX, HTML, XLSX/CSV, Scanned)
    ↓
Stage 1 — File Intake
    Validate file type
    Extract file metadata (filename, author, date, total pages)
    Set document status → "processing"

    ↓
Stage 2 — Document Parsing (Docling / Unstructured)
    Separate into 3 streams:
        ├── Text blocks  (page, section title, y_position)
        ├── Tables       (page, row/col structure, y_position)
        └── Images       (page, bounding box, y_position)
             (photos, charts, graphs, diagrams — all treated as images)

    ↓
Stage 3 — Chunking + Tree Building
    Group ALL elements by section using page + y_position proximity
    Assign chunk_id + parent_chunk_id to EVERY chunk upfront
    (full tree built in memory — before any storing begins)

    Text  → parent chunk (~1024 tokens) + child chunks (~256 tokens each)
    Table → atomic child chunk (no splitting)
    Image → atomic child chunk (no splitting)

    Every chunk gets:
        chunk_id         (unique, generated now)
        parent_chunk_id  (points to section parent)
        chunk_type       (parent / child)

    ↓
Stage 4 — Split into Concurrent Tracks

    Track 1: Text + Table chunks        Track 2: Image chunks
    ─────────────────────────────       ──────────────────────────────
    Text: LLM summarize if long         Optimize image (Pillow):
    Text: use as-is if normal               resize → max 1280px
    Table: convert to markdown              convert → WebP
    Table: LLM summarize if complex         quality 75% → check size
                                            over 400KB? → reduce (65→55→45)
                                            encode → base64 string
                                        ↓
    Assemble metadata per chunk         VLM (GPT-4o) — single call:
    {                                       classify type + generate caption
      chunk_id,                         ↓
      parent_chunk_id,                  Assemble metadata per chunk
      chunk_type,                       {
      source_file,                        chunk_id,
      page_number,                        parent_chunk_id,
      section_title,                      chunk_type,
      modality: "text"|"table",           source_file,
      content: "text or markdown",        page_number,
      asset_base64: null,                 section_title,
      language: "en",                     modality: "image",
      created_at: timestamp               content: "VLM caption text",
    }                                     asset_base64: "data:image/webp;base64,...",
    ↓                                     language: "en",
    Embed content:                        created_at: timestamp
        Dense  → BGE-large-en → vector  }
        Sparse → BM25 tokens            ↓
    ↓                                   Embed caption:
    Store in Qdrant ✓                       Dense  → BGE-large-en → vector
    (done early)                            Sparse → BM25 tokens
                                        ↓
                                        Store in Qdrant ✓
                                        (done after optimization + VLM)

    ↓ both tracks complete (asyncio.gather)
Stage 5 — Completion
    Both tracks done → set document status → "completed"
    Either track fails → set document status → "failed" + log error
```

**Qdrant collection — single collection "astrynox_chunks", all modalities mixed:**
```
sec_chunk_A       text   parent: null        content: "full section text..."  base64: null
child_chunk_1     text   parent: sec_chunk_A content: "Revenue grew 24%..."   base64: null
child_chunk_2     text   parent: sec_chunk_A content: "APAC contributed..."   base64: null
child_chunk_tbl_1 table  parent: sec_chunk_A content: "| Region | Revenue..." base64: null
child_chunk_img_1 image  parent: sec_chunk_A content: "Bar chart showing..."  base64: "data:image/webp;..."
```

**Full Ingestion Flow:**
```
Raw File
  → Parse (3 streams: text / table / image)
  → Chunk + Build full tree in memory (assign all IDs upfront)
  → Split into concurrent tracks (asyncio.gather)
      Track 1: text/table → LLM if needed → metadata → embed → store
      Track 2: image → optimize → VLM caption → metadata → embed → store
  → Both complete → document status "completed"
```

---

### 6.3 Retrieval Pipeline (Phase 1)

```
User Query (English)
    ↓
Stage 1 — Query Intake
    Clean + normalize query
    Detect query type:
        ├── Visual   → "show me", "display", "chart", "image"
        ├── Summary  → "summarize", "overview", "brief"
        └── Factual  → everything else

    ↓
Stage 2 — Redis Cache Check (2 layers)
    L1 Answer Cache
        key:   hash(query)
        value: full answer + citations
        TTL:   1 hour
        HIT  → return answer immediately (skip everything below)
        ↓ MISS
    L2 Embedding Cache
        key:   hash(query string)
        value: dense vector
        TTL:   7 days
        HIT  → use cached vector, skip to Stage 4
        ↓ MISS

    ↓
Stage 3 — Query Embedding
    Dense  → BAAI/bge-large-en-v1.5 (local) → query vector (1024 dim)
    Sparse → BM25 tokens
    Write dense vector → L2 Embedding Cache

    ↓
Stage 4 — Hybrid Retrieval (parallel)
    Dense search  → Qdrant ANN search → top-k semantic matches
    Sparse search → BM25 keyword search → top-k keyword matches
    Visual query? → add Qdrant payload filter: modality = "image"

    ↓
Stage 5 — RRF Fusion
    score(chunk) = 1/(rank_dense + 60) + 1/(rank_sparse + 60)
    Unified ranked list → final top-k chunks

    ↓
Stage 6 — Relevance Threshold Check
    RRF score ≥ threshold → keep chunk ✓
    RRF score < threshold → discard chunk ✗
    0 chunks pass:
        → return "I don't have enough information to answer this."
        → skip LLM call entirely (save cost)
        → do NOT write to L1 cache

    ↓
Stage 7 — Context Assembly
    For each passing chunk:
        modality = "text"  → use content field
        modality = "table" → use content field (markdown)
        modality = "image" → use content (caption) + asset_base64 from payload
    Fetch parent chunks for child chunks
    Deduplicate: multiple children from same parent → fetch parent once only
    Assign citation numbers [1][2][3]...

    ↓
Stage 8 — LLM Generation (GPT-4o)
    System prompt:
        "Answer using ONLY the provided context.
         Cite sources inline as [1][2][3].
         If context is insufficient, say so clearly.
         Do not make up information."
    Visual query → pass image base64 directly to GPT-4o vision
    GPT-4o generates answer with inline citations

    ↓
Stage 9 — Citation Builder
    [N] modality = "text"
        → source_file, page_number, section_title
        → content snippet
    [N] modality = "table"
        → source_file, page_number, section_title
        → render markdown table
    [N] modality = "image"
        → source_file, page_number, section_title
        → render image from asset_base64 (no external fetch needed)

    ↓
Stage 10 — Cache + Return
    Write full answer + citations → L1 Answer Cache (TTL: 1hr)
    Return to user:
        ├── Answer text with inline [1][2][3]
        └── Citations block (text snippets / rendered tables / rendered images)
```

**Cache Invalidation:**
```
New document ingested:
    ├── Flush L1 Answer Cache    (answers may now be outdated)
    └── Keep L2 Embedding Cache  (query vectors don't change)
```

**Full Retrieval Flow:**
```
Query
  → Clean + detect type
  → L1 cache check           → HIT: return immediately
  → L2 cache check           → HIT: skip embedding
  → Embed query (BGE local, dense + BM25 sparse)
  → Write to L2 cache
  → Hybrid retrieval parallel (dense ANN + BM25)
       └── Visual query? → filter to image chunks only
  → RRF fusion → unified top-k
  → Relevance threshold check
       └── No pass? → return "not enough info" (skip LLM, skip cache)
  → Context assembly + parent deduplication
       └── Images → load base64 from Qdrant payload directly
  → Assign citation numbers
  → GPT-4o generation with inline citations
  → Citation builder (text / table markdown / image base64 rendered)
  → Write to L1 cache
  → Return answer + citations
```

**Deferred to Phase 2:**
```
├── Cross-encoder reranker (after RRF)
├── Query rewriting (before embedding)
└── L3 Retrieval Cache (top-k chunk IDs keyed by embedding vector)
```

---

### 6.4 Cache Invalidation
- On new document ingestion: flush L1 Answer Cache
- L2 Embedding Cache: retained (query embeddings are stable)

---

## 7. Functional Requirements

### 7.1 Authentication
- FR-01: User can register with email and password
- FR-02: User can log in with email and password
- FR-03: User can log in with Google OAuth2 (no OTP required)
- FR-04: OTP verification via Resend on email/password login only
- FR-05: JWT token issued on successful authentication
- FR-06: Token refresh mechanism

### 7.2 Admin — Document Management
- FR-07: Admin can upload documents (PDF, DOCX, PPTX, HTML, XLSX/CSV, scanned)
- FR-08: Admin can view list of all ingested documents with status
- FR-09: Admin can delete a document (removes from vector DB and storage)
- FR-10: Admin can trigger company website scraping
- FR-11: Admin receives ingestion status (processing / completed / failed)

### 7.3 Chat Interface
- FR-12: Employee can type a query and receive an answer
- FR-13: Answer includes inline citations [1][2][3]
- FR-14: Citations section shows source file, page number, section title
- FR-15: Image and chart citations render the original visual asset
- FR-16: Table citations render the original table structure
- FR-17: System returns "I don't have enough information" when no relevant context found
- FR-18: Query response time target: under 5 seconds (cache hit: under 500ms)

### 7.4 Web Scraping
- FR-19: Admin can input company website URL to scrape
- FR-20: System scrapes and ingests HTML content through the ingestion pipeline
- FR-21: Scraped content is chunked, embedded, and stored identically to uploaded documents

### 7.5 API
- FR-22: REST API exposes query endpoint for external integrations
- FR-23: REST API exposes document upload endpoint for admin use
- FR-24: All API endpoints require authentication

---

## 8. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Query response time | < 5 seconds (cold), < 500ms (cache hit) |
| Ingestion throughput | 100 documents total for MVP |
| Uptime (MVP) | Best effort (local) |
| Uptime (Production) | 99.5% |
| Security | JWT auth, OTP verification, no PII logged |
| Scalability | Architecture must support AWS migration without pipeline changes |
| Observability | Basic logging per ingestion job and query |

---

## 9. User Stories

### Authentication
- US-01: As an employee, I want to log in with my email and password so I can access the assistant securely.
- US-02: As an employee, I want to verify my email login with an OTP so my account is protected.
- US-03: As an employee, I want to log in with my Google account without extra steps so the process is fast and seamless.

### Admin — Document Management
- US-04: As an admin, I want to upload company documents so employees can query them.
- US-05: As an admin, I want to see the ingestion status of each document so I know when it's ready.
- US-06: As an admin, I want to delete a document so outdated content is removed from the system.
- US-07: As an admin, I want to trigger a website scrape so the company website content is always up to date.

### Chat Interface
- US-08: As an employee, I want to ask questions in plain English and get accurate answers.
- US-09: As an employee, I want to see citations with every answer so I can verify the source.
- US-10: As an employee, I want to see the original image or chart when it's cited so I can review the visual data.
- US-11: As an employee, I want to see the original table when it's cited so I can read the full data.
- US-12: As an employee, I want a clear message when the system cannot find relevant information.

---

## 10. Sprint Plan

### Sprint 1 — Week 1: Foundation & Auth
**Goal:** Project scaffolding, authentication system, and admin document upload UI live.

| Task | Description |
|------|-------------|
| SP1-01 | Initialize FastAPI project structure |
| SP1-02 | Initialize Next.js project structure |
| SP1-03 | Set up Docker Compose (FastAPI, Redis, Qdrant) |
| SP1-04 | Implement email/password registration and login |
| SP1-05 | Implement Google OAuth2 login (no OTP) |
| SP1-06 | Integrate Resend OTP for email/password login only |
| SP1-07 | JWT token issuance and refresh |
| SP1-08 | Admin document upload endpoint (file validation, metadata extraction) |
| SP1-09 | Admin dashboard UI (document list, upload form, status display) |
| SP1-10 | Basic login and register pages (Next.js) |

**Definition of Done:** User can register, log in (email or Google), verify OTP, and admin can upload a document and see it listed.

---

### Sprint 2 — Week 2: Ingestion Pipeline
**Goal:** Full ingestion pipeline operational — documents parsed, chunked, processed, embedded, and stored in Qdrant.

| Task | Description |
|------|-------------|
| SP2-01 | Integrate Docling / Unstructured for document parsing |
| SP2-02 | Stream separation into 3 streams (text, tables, images) |
| SP2-03 | Implement OCR for scanned documents (Tesseract) |
| SP2-04 | Hierarchical chunking + parent-child tree builder (assign all IDs upfront) |
| SP2-05 | Image optimization layer (Pillow: resize → WebP → quality reduction → base64) |
| SP2-06 | Concurrent track split (asyncio.gather — Track 1: text/table, Track 2: image) |
| SP2-07 | VLM integration (GPT-4o) — single call for image classify + caption |
| SP2-08 | Table markdown extraction + LLM summarization for complex tables |
| SP2-09 | LLM summarization for long text chunks |
| SP2-10 | Per-chunk metadata assembly (denormalized, chunk_id + parent_chunk_id) |
| SP2-11 | Dense embedding — BAAI/bge-large-en-v1.5 local model (sentence-transformers) |
| SP2-12 | Sparse embedding (BM25) |
| SP2-13 | Store vectors + metadata + base64 in Qdrant single collection |
| SP2-14 | Web scraping (BeautifulSoup + Playwright) → feed into ingestion pipeline |
| SP2-15 | Ingestion status updates (processing / completed / failed) |

**Definition of Done:** Admin uploads a PDF with text, tables, and images — all chunks embedded and stored in Qdrant with full metadata, base64 images in payload, correct parent-child tree relationships.

---

### Sprint 3 — Week 3: Retrieval Pipeline & Redis Cache
**Goal:** Full retrieval pipeline operational — query returns ranked, relevant chunks with Redis caching.

| Task | Description |
|------|-------------|
| SP3-01 | Query intake — clean, normalize, detect type |
| SP3-02 | Redis L1 Answer Cache (set, get, invalidate on ingestion) |
| SP3-03 | Redis L2 Embedding Cache (set, get) |
| SP3-04 | Query dense embedding (BAAI/bge-large-en-v1.5 local) |
| SP3-05 | Query sparse embedding (BM25) |
| SP3-06 | Qdrant dense ANN search |
| SP3-07 | BM25 keyword search |
| SP3-08 | RRF fusion — merge and rank dense + sparse results |
| SP3-09 | Relevance threshold check (discard low-score chunks) |
| SP3-10 | Context assembly (fetch text/table content, load base64 from Qdrant for image chunks) |
| SP3-11 | Parent chunk deduplication |

**Definition of Done:** Query runs through full retrieval — cache checked, hybrid search executed, results fused and filtered, context assembled correctly.

---

### Sprint 4 — Week 4: Generation, Citations & Polish
**Goal:** Full end-to-end system working — LLM generates cited answers, frontend chat complete, system tested and ready.

| Task | Description |
|------|-------------|
| SP4-01 | LLM generation (GPT-4o) with citation prompt |
| SP4-02 | Citation builder (text snippet / markdown table / base64 image rendered inline) |
| SP4-03 | Write answer to L1 Answer Cache |
| SP4-04 | Chat UI (Next.js) — query input, streaming response, citations |
| SP4-05 | Visual citation rendering (images rendered inline from base64) |
| SP4-06 | Table citation rendering (markdown table) |
| SP4-07 | "Not enough information" response handling in UI |
| SP4-08 | REST API query endpoint (for external integrations) |
| SP4-09 | End-to-end testing (ingestion → retrieval → generation → citation) |
| SP4-10 | Basic logging per ingestion job and query |
| SP4-11 | Docker Compose final configuration |
| SP4-12 | AWS deployment preparation (S3 config, env var setup) |

**Definition of Done:** Employee logs in, asks a question, receives a cited answer with rendered visual citations. Admin uploads a document and it becomes queryable within minutes.

---

## 11. Acceptance Criteria

| ID | Criteria |
|----|----------|
| AC-01 | User can log in via email/password with OTP and receive a JWT |
| AC-02 | User can log in via Google OAuth2 without OTP and receive a JWT |
| AC-03 | Admin can upload a PDF and see it move to "completed" status |
| AC-04 | Admin can delete a document and it is removed from Qdrant |
| AC-05 | A query about a document returns a relevant answer with citations |
| AC-06 | An image-based answer includes the rendered original image in citations |
| AC-07 | A table-based answer includes the rendered original table in citations |
| AC-08 | A query with no matching context returns a "not enough information" message |
| AC-09 | Same query answered twice — second response served from L1 cache |
| AC-10 | Cache L1 is cleared when a new document is ingested |
| AC-11 | Website scraping ingests content and makes it queryable |
| AC-12 | Query response time is under 5 seconds for a cold query |

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GPT-4o API cost overrun during ingestion | Medium | Medium | Batch VLM/LLM calls, set rate limits, monitor token usage |
| OCR quality poor for scanned documents | Medium | Medium | Test with Tesseract early, fallback to manual text extraction |
| Qdrant hybrid search misconfiguration | Low | High | Test sparse + dense indexing in Sprint 2 with sample data |
| Ingestion pipeline too slow for large files | Low | Medium | Run ingestion as async background job with status updates |
| Redis cache stale after document update | Medium | Medium | Flush L1 on every ingestion event |
| 4-week timeline too aggressive | Medium | High | Drop web scraping from MVP if behind schedule |

---

## 13. Phase 2 Backlog

| Feature | Description |
|---------|-------------|
| Cross-encoder reranker | Improve retrieval quality after RRF |
| Query rewriting | Rewrite vague queries before embedding |
| L3 Retrieval Cache | Cache top-k chunk IDs keyed by embedding vector |
| Conversation memory | Multi-turn context across queries |
| Multilingual support | Sinhala and Tamil query handling |
| Analytics dashboard | Query volume, cache hit rate, top queries |
| Role-based access control | Fine-grained permissions beyond Admin/Employee |
| AWS S3 asset storage | Replace base64 in Qdrant payload with S3 asset paths for production scale |
| Mobile application | iOS/Android interface |

---

## 14. Definition of Done (Project-Level)

A sprint item is considered done when:
- Code is written and reviewed
- Feature works end-to-end in local environment
- Basic error handling is in place
- No breaking changes to existing features
- Relevant API endpoint is tested manually

---

*Astrynox AI — PRD v1.0 | Prepared for Agile Scrum Sprint Planning*
