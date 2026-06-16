# Software Design Document (SDD)
# Astrynox AI — Hybrid Multimodal RAG System

**Version:** 1.0  
**Project:** Astrynox AI  
**Author:** Brayan K. Jayawardhana  
**Status:** Active  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [High-Level Architecture](#3-high-level-architecture)
4. [Component Design](#4-component-design)
5. [Frontend Design](#5-frontend-design)
6. [Backend API Design](#6-backend-api-design)
7. [Ingestion Pipeline Design](#7-ingestion-pipeline-design)
8. [Retrieval Pipeline Design](#8-retrieval-pipeline-design)
9. [Data Design](#9-data-design)
10. [Authentication Design](#10-authentication-design)
11. [Security Design](#11-security-design)
12. [Error Handling](#12-error-handling)
13. [Folder Structure](#13-folder-structure)
14. [Environment Configuration](#14-environment-configuration)

---

## 1. Introduction

### 1.1 Purpose
This Software Design Document describes the technical architecture, component design, data models, API contracts, and pipeline flows for **Astrynox AI** — an enterprise internal knowledge assistant built on a Hybrid Multimodal RAG pipeline.

### 1.2 Scope
This document covers the complete system design for both Phase 1 (MVP) and Phase 2 (Enhanced), including all backend services, frontend interfaces, ingestion and retrieval pipelines, and deployment architecture.

### 1.3 Definitions

| Term | Definition |
|------|-----------|
| RAG | Retrieval-Augmented Generation — combining document retrieval with LLM generation |
| Hybrid RAG | Combines dense (semantic) and sparse (keyword) retrieval |
| Multimodal | Handles text, tables, and images within the same pipeline |
| VLM | Vision Language Model — processes images and generates text descriptions |
| Dense Embedding | Fixed-size vector representation capturing semantic meaning |
| Sparse Embedding | BM25 token representation capturing keyword frequency |
| RRF | Reciprocal Rank Fusion — algorithm to merge ranked lists from multiple retrievers |
| Chunk | A discrete unit of document content stored and retrieved independently |
| Parent Chunk | A large context chunk (~1024 tokens) representing a document section |
| Child Chunk | A smaller chunk (~256 tokens) nested under a parent |
| Atomic Chunk | An indivisible chunk — used for images and tables |

---

## 2. System Overview

Astrynox AI ingests company documents and website content, processes them through a multimodal pipeline, stores them in a vector database, and enables employees to query the knowledge base through a chat interface — receiving accurate, cited answers.

### 2.1 Key Design Principles

- **Separation of concerns** — ingestion and retrieval are independent services
- **Async-first** — ingestion uses concurrent tracks to avoid bottlenecks
- **Self-contained chunks** — every chunk carries all metadata needed for citation without extra lookups
- **Cache-first retrieval** — Redis cache checked before any embedding or search
- **Modality-agnostic storage** — all chunk types stored in a single Qdrant collection differentiated by `modality` field

---

## 3. High-Level Architecture

### 3.1 System Architecture Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        EMP[Employee Browser]
        ADM[Admin Browser]
    end

    subgraph Frontend["Frontend — Next.js"]
        CHAT[Chat Interface]
        ADMUI[Admin Dashboard]
        AUTH[Auth Pages]
    end

    subgraph Backend["Backend — FastAPI"]
        AUTHSVC[Auth Service]
        INGSVC[Ingestion Service]
        RETSVC[Retrieval Service]
        GENSVC[Generation Service]
        SCRSVC[Scraping Service]
    end

    subgraph Storage["Storage Layer"]
        QDRANT[(Qdrant\nVector DB)]
        REDIS[(Redis\nCache)]
        SQLDB[(SQLite / PostgreSQL\nUser + Document DB)]
    end

    subgraph External["External APIs"]
        OPENAI[OpenAI GPT-4o\nVLM + LLM]
        RESEND[Resend\nOTP Email]
        GOOGLE[Google OAuth2]
    end

    subgraph Local["Local Models"]
        BGE[BAAI/bge-large-en-v1.5\nDense Embedding]
        BM25[BM25\nSparse Embedding]
    end

    subgraph DB["Relational DB"]
        PG[(PostgreSQL\nUsers + Documents + OTP)]
    end

    EMP --> CHAT
    ADM --> ADMUI
    EMP --> AUTH
    ADM --> AUTH

    CHAT --> RETSVC
    CHAT --> GENSVC
    ADMUI --> INGSVC
    ADMUI --> SCRSVC
    AUTH --> AUTHSVC

    AUTHSVC --> PG
    AUTHSVC --> RESEND
    AUTHSVC --> GOOGLE

    INGSVC --> OPENAI
    INGSVC --> BGE
    INGSVC --> BM25
    INGSVC --> QDRANT
    INGSVC --> PG

    SCRSVC --> INGSVC

    RETSVC --> REDIS
    RETSVC --> BGE
    RETSVC --> BM25
    RETSVC --> QDRANT

    GENSVC --> OPENAI
    GENSVC --> REDIS
```

---

### 3.2 Request Flow Overview

```mermaid
graph LR
    subgraph Ingestion["Ingestion Flow (Admin)"]
        A1[Upload File] --> A2[Parse Document]
        A2 --> A3[Chunk + Tree]
        A3 --> A4[Concurrent Processing]
        A4 --> A5[Embed + Store Qdrant]
    end

    subgraph Retrieval["Retrieval Flow (Employee)"]
        B1[User Query] --> B2{Cache Hit?}
        B2 -->|Yes| B6[Return Cached Answer]
        B2 -->|No| B3[Embed Query]
        B3 --> B4[Hybrid Search]
        B4 --> B5[RRF + Threshold]
        B5 --> B6[Assemble + Generate + Cite]
    end
```

---

## 4. Component Design

### 4.1 Component Diagram

```mermaid
graph TB
    subgraph FastAPI["FastAPI Backend"]
        subgraph API["API Layer (Routes)"]
            R1[auth.py]
            R2[documents.py]
            R3[query.py]
            R4[scraping.py]
        end

        subgraph SVC["Service Layer"]
            subgraph ING["Ingestion Service"]
                I1[parser.py]
                I2[chunker.py]
                I3[image_optimizer.py]
                I4[vlm.py]
                I5[embedder.py]
                I6[storer.py]
            end

            subgraph RET["Retrieval Service"]
                R5[cache.py]
                R6[searcher.py]
                R7[fusion.py]
                R8[assembler.py]
            end

            subgraph GEN["Generation Service"]
                G1[llm.py]
                G2[citation_builder.py]
            end

            S1[scraper.py]
            A1[auth_service.py]
        end

        subgraph CORE["Core"]
            C1[config.py]
            C2[security.py]
            C3[logging.py]
            C4[dependencies.py]
        end

        subgraph MDL["Models"]
            M1[user.py]
            M2[document.py]
            M3[chunk.py]
        end
    end

    subgraph NextJS["Next.js Frontend"]
        subgraph PAGES["Pages / App Router"]
            P1[app/auth/login]
            P2[app/auth/register]
            P3[app/chat]
            P4[app/admin/documents]
            P5[app/admin/scraping]
        end

        subgraph COMP["Components"]
            CP1[ChatInput]
            CP2[ChatMessage]
            CP3[CitationBlock]
            CP4[ImageCitation]
            CP5[TableCitation]
            CP6[DocumentList]
            CP7[UploadForm]
        end

        subgraph LIB["Lib"]
            L1[api.ts]
            L2[auth.ts]
            L3[types.ts]
        end
    end
```

---

### 4.2 Component Responsibilities

| Component | File | Responsibility |
|-----------|------|---------------|
| Parser | `ingestion/parser.py` | Parse PDF/DOCX/PPTX/HTML/XLSX via Docling, OCR for scanned docs via Tesseract, extract text/table/image streams with position metadata |
| Chunker | `ingestion/chunker.py` | Group elements by section, build parent-child tree, assign chunk_id + parent_chunk_id upfront |
| Image Optimizer | `ingestion/image_optimizer.py` | Resize → WebP → quality reduction → base64 encode |
| VLM | `ingestion/vlm.py` | GPT-4o single call per image: classify type + generate caption |
| Embedder (ingestion) | `ingestion/embedder.py` | BGE-large-en-v1.5 dense embedding + BM25 sparse embedding at ingestion |
| Storer | `ingestion/storer.py` | Upsert chunk vectors + metadata + base64 into Qdrant |
| Cache | `retrieval/cache.py` | Redis L1 Answer Cache + L2 Embedding Cache read/write/invalidate |
| Searcher | `retrieval/searcher.py` | Qdrant ANN dense search + BM25 sparse search, parallel execution |
| Fusion | `retrieval/fusion.py` | RRF merge, relevance threshold filter |
| Assembler | `retrieval/assembler.py` | Fetch chunks from Qdrant, parent deduplication, load base64, assign citation numbers |
| LLM | `generation/llm.py` | GPT-4o generation with citation system prompt |
| Citation Builder | `generation/citation_builder.py` | Build text/table/image citation blocks |
| Scraper | `scraper.py` | Playwright + BeautifulSoup web scraping, feed HTML into ingestion |
| Auth Service | `auth_service.py` | JWT issuance, OTP generation/verification, Google OAuth2 |

---

## 5. Frontend Design

### 5.1 Page Structure

```mermaid
graph TD
    ROOT["/"] --> LOGIN["/auth/login"]
    ROOT --> REGISTER["/auth/register"]
    LOGIN --> OTP["/auth/verify-otp"]
    LOGIN --> GOOGLE["Google OAuth2 Redirect"]
    OTP --> CHAT["/chat"]
    GOOGLE --> CHAT

    CHAT --> ADMIN["/admin/documents"]
    ADMIN --> SCRAPING["/admin/scraping"]
```

### 5.2 Chat Page Component Tree

```mermaid
graph TD
    CHATPAGE["ChatPage"] --> SIDEBAR["Sidebar\n(history placeholder)"]
    CHATPAGE --> MAIN["ChatMain"]
    MAIN --> MESSAGES["MessageList"]
    MAIN --> INPUT["ChatInput"]
    MESSAGES --> MSG["ChatMessage\n(per message)"]
    MSG --> INLINE["InlineCitations\n[1][2][3]"]
    MSG --> CITBLOCK["CitationBlock"]
    CITBLOCK --> TXTCIT["TextCitation\n(source + snippet)"]
    CITBLOCK --> TBLCIT["TableCitation\n(markdown table)"]
    CITBLOCK --> IMGCIT["ImageCitation\n(base64 render)"]
```

### 5.3 Admin Dashboard Component Tree

```mermaid
graph TD
    ADMINPAGE["AdminPage"] --> DOCLIST["DocumentList"]
    ADMINPAGE --> UPLOAD["UploadForm"]
    ADMINPAGE --> SCRAPEBTN["ScrapeTrigger"]
    DOCLIST --> DOCROW["DocumentRow\n(name, status, date, delete)"]
    DOCROW --> STATUS["StatusBadge\n(processing/completed/failed)"]
```

---

## 6. Backend API Design

### 6.1 API Endpoints

#### Authentication

| Method | Endpoint | Auth | Description |
|--------|---------|------|-------------|
| POST | `/api/auth/register` | None | Register with email + password |
| POST | `/api/auth/login` | None | Login with email + password → sends OTP |
| POST | `/api/auth/verify-otp` | None | Verify OTP → returns JWT |
| POST | `/api/auth/google` | None | Google OAuth2 login → returns JWT |
| POST | `/api/auth/refresh` | JWT | Refresh access token |
| POST | `/api/auth/logout` | JWT | Invalidate token |

#### Documents (Admin only)

| Method | Endpoint | Auth | Description |
|--------|---------|------|-------------|
| POST | `/api/documents/upload` | JWT + Admin | Upload document, trigger ingestion |
| GET | `/api/documents/` | JWT + Admin | List all documents with status |
| GET | `/api/documents/{id}` | JWT + Admin | Get single document details |
| DELETE | `/api/documents/{id}` | JWT + Admin | Delete document + remove from Qdrant |
| GET | `/api/documents/{id}/status` | JWT + Admin | Poll ingestion status |

#### Query

| Method | Endpoint | Auth | Description |
|--------|---------|------|-------------|
| POST | `/api/query` | JWT | Submit query, returns answer + citations |

#### Scraping (Admin only)

| Method | Endpoint | Auth | Description |
|--------|---------|------|-------------|
| POST | `/api/scraping/trigger` | JWT + Admin | Trigger website scrape |
| GET | `/api/scraping/status` | JWT + Admin | Check scraping job status |

---

### 6.2 Request / Response Schemas

**POST /api/auth/login**
```json
Request:
{
  "email": "user@company.com",
  "password": "securepassword"
}

Response (200):
{
  "message": "OTP sent to email",
  "otp_token": "temp_token_for_otp_verification"
}
```

**POST /api/auth/verify-otp**
```json
Request:
{
  "otp_token": "temp_token",
  "otp_code": "482910"
}

Response (200):
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@company.com",
    "role": "employee"
  }
}
```

**POST /api/documents/upload**
```json
Request: multipart/form-data
  file: <binary>
  filename: "annual_report_2024.pdf"

Response (202):
{
  "document_id": "uuid",
  "filename": "annual_report_2024.pdf",
  "status": "processing",
  "created_at": "2026-06-16T10:00:00Z"
}
```

**POST /api/query**
```json
Request:
{
  "query": "What was the Q3 revenue for APAC?",
  "query_type": "factual"
}

Response (200):
{
  "answer": "The Q3 revenue for APAC was $4.2M [1], representing a 31% growth [2].",
  "citations": [
    {
      "id": 1,
      "source_file": "annual_report_2024.pdf",
      "page_number": 12,
      "section_title": "Revenue Overview",
      "modality": "text",
      "content": "APAC region contributed $4.2M in Q3...",
      "asset_base64": null
    },
    {
      "id": 2,
      "source_file": "annual_report_2024.pdf",
      "page_number": 7,
      "section_title": "Regional Breakdown",
      "modality": "image",
      "content": "Bar chart showing Q3 revenue by region. APAC leads at $4.2M with 31% growth.",
      "asset_base64": "data:image/webp;base64,iVBORw0..."
    }
  ],
  "from_cache": false,
  "response_time_ms": 2340
}
```

---

## 7. Ingestion Pipeline Design

### 7.1 Full Ingestion Flow

```mermaid
flowchart TD
    A([Raw File Upload]) --> B[Stage 1: File Intake\nValidate type\nExtract metadata\nSet status: processing]

    B --> C[Stage 2: Document Parsing\nDocling / Unstructured\nOCR if scanned]

    C --> D1[Text Blocks\npage, section, y_pos]
    C --> D2[Tables\npage, row/col, y_pos]
    C --> D3[Images\npage, bounding box, y_pos]

    D1 & D2 & D3 --> E[Stage 3: Chunking + Tree Building\nGroup by section via page + y_position\nAssign chunk_id + parent_chunk_id upfront\nBuild full parent-child tree in memory]

    E --> F{Split Concurrent Tracks\nasyncio.gather}

    F --> G[Track 1: Text + Table]
    F --> H[Track 2: Image]

    G --> G1{Too long?}
    G1 -->|Yes| G2[LLM Summarization\nGPT-4o]
    G1 -->|No| G3[Use as-is]
    G2 & G3 --> G4{Table?}
    G4 -->|Yes| G5[Convert to Markdown\nLLM if complex]
    G4 -->|No| G6[Text content ready]
    G5 & G6 --> G7[Assemble Metadata\nchunk_id, parent_id, modality,\ncontent, asset_base64: null]
    G7 --> G8[Dense Embed\nBGE-large-en-v1.5]
    G8 --> G9[Sparse Embed\nBM25]
    G9 --> G10[(Store in Qdrant\nastrynox_chunks)]

    H --> H1[Image Optimization\nPillow]
    H1 --> H2[Resize max 1280px\nMaintain aspect ratio]
    H2 --> H3[Convert to WebP\nQuality 75%]
    H3 --> H4{Under 400KB?}
    H4 -->|No| H5[Reduce quality\n65 → 55 → 45]
    H5 --> H4
    H4 -->|Yes| H6[Encode to base64]
    H6 --> H7[VLM Call - GPT-4o\nSingle call:\nclassify type + generate caption]
    H7 --> H8[Assemble Metadata\nchunk_id, parent_id, modality: image\ncontent: caption, asset_base64: webp]
    H8 --> H9[Dense Embed\nBGE-large-en-v1.5\nembed caption text]
    H9 --> H10[Sparse Embed\nBM25]
    H10 --> G10

    G10 --> I{Both tracks\ncomplete?}
    I -->|Yes| J[Set document status: completed]
    I -->|No - error| K[Set document status: failed\nLog error + chunk_id]
```

---

### 7.2 Hierarchical Chunk Tree Structure

```mermaid
graph TD
    DOC["Document: annual_report_2024.pdf"] --> SEC1["Parent: sec_chunk_A\nSection 3 — Revenue Analysis\npage 7, ~1024 tokens\nmodality: text"]
    DOC --> SEC2["Parent: sec_chunk_B\nSection 4 — Regional Breakdown\npage 9, ~1024 tokens\nmodality: text"]

    SEC1 --> C1["Child: child_chunk_1\nmodality: text\n~256 tokens\nparent: sec_chunk_A"]
    SEC1 --> C2["Child: child_chunk_2\nmodality: text\n~256 tokens\nparent: sec_chunk_A"]
    SEC1 --> C3["Child: child_chunk_img_1\nmodality: image\nVLM caption\nasset_base64: webp\nparent: sec_chunk_A"]

    SEC2 --> C4["Child: child_chunk_3\nmodality: text\n~256 tokens\nparent: sec_chunk_B"]
    SEC2 --> C5["Child: child_chunk_tbl_1\nmodality: table\nmarkdown table\nparent: sec_chunk_B"]
```

---

### 7.3 Concurrent Tracks Timing

```mermaid
gantt
    title Ingestion Concurrent Tracks (per document)
    dateFormat SSS
    axisFormat %Lms

    section Track 1 - Text & Table
    Parse + Chunk + Tree Build   :active, a1, 000, 200ms
    LLM summarization (if needed):a2, after a1, 300ms
    Metadata assembly            :a3, after a2, 50ms
    Dense + Sparse Embed         :a4, after a3, 200ms
    Store in Qdrant              :done, a5, after a4, 100ms

    section Track 2 - Image
    Parse + Chunk + Tree Build   :active, b1, 000, 200ms
    Image optimization (Pillow)  :b2, after b1, 150ms
    VLM caption + classify       :b3, after b2, 2000ms
    Metadata assembly            :b4, after b3, 50ms
    Dense + Sparse Embed         :b5, after b4, 200ms
    Store in Qdrant              :done, b6, after b5, 100ms
```

---

## 8. Retrieval Pipeline Design

### 8.1 Full Retrieval Flow

```mermaid
flowchart TD
    A([User Query]) --> B[Stage 1: Query Intake\nClean + normalize\nDetect type: factual / visual / summary]

    B --> C{Stage 2: L1 Answer Cache\nRedis - key: hash query\nTTL: 1 hour}
    C -->|HIT| Z([Return Cached Answer\nInstantly])
    C -->|MISS| D{Stage 2: L2 Embedding Cache\nRedis - key: hash query string\nTTL: 7 days}
    D -->|HIT| F[Use cached vector\nSkip embedding call]
    D -->|MISS| E[Stage 3: Query Embedding\nBGE-large-en-v1.5 dense vector\nBM25 sparse tokens\nWrite to L2 cache]

    E & F --> G[Stage 4: Hybrid Retrieval\nParallel execution]

    G --> G1[Dense Search\nQdrant ANN\ntop-k semantic matches]
    G --> G2[Sparse Search\nBM25 keyword\ntop-k keyword matches]

    G1 & G2 --> H[Stage 5: RRF Fusion\nscore = 1 over rank_dense+60\n+ 1 over rank_sparse+60\nUnified ranked top-k]

    H --> I{Stage 6: Relevance\nThreshold Check}
    I -->|All below threshold| J([Return: I don't have\nenough information\nNo LLM call\nNo cache write])
    I -->|Some pass| K[Stage 7: Context Assembly\nFetch chunk content from Qdrant\nFetch parent chunks\nDeduplicate parents\nLoad base64 for image chunks\nAssign citation numbers 1 2 3]

    K --> L{Visual query?}
    L -->|Yes| L1[Pass base64 image\nto GPT-4o vision]
    L -->|No| L2[Pass text context only]

    L1 & L2 --> M[Stage 8: LLM Generation\nGPT-4o\nAnswer with inline citations]

    M --> N[Stage 9: Citation Builder\nText: source + snippet\nTable: render markdown\nImage: render from base64]

    N --> O[Stage 10: Write to L1 Cache\nTTL: 1 hour]

    O --> P([Return Answer + Citations])
```

---

### 8.2 Redis Cache Architecture

```mermaid
graph TB
    Q[User Query] --> L1

    subgraph REDIS["Redis Cache"]
        L1["L1 — Answer Cache\nkey: hash(query)\nvalue: {answer, citations}\nTTL: 1 hour\nInvalidate: on new doc ingest"]
        L2["L2 — Embedding Cache\nkey: hash(query string)\nvalue: dense vector 1024 dim\nTTL: 7 days\nInvalidate: never"]
    end

    L1 -->|HIT| R1([Return answer])
    L1 -->|MISS| L2
    L2 -->|HIT| R2([Use vector, skip embed])
    L2 -->|MISS| R3([Call BGE model])

    subgraph PHASE2["Phase 2 Addition"]
        L3["L3 — Retrieval Cache\nkey: hash(embedding vector)\nvalue: top-k chunk IDs\nTTL: 30 mins"]
    end
```

---

### 8.3 Visual Query Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant Q as Qdrant
    participant GPT as GPT-4o

    U->>API: "Show me the revenue chart"
    API->>API: Detect type: visual
    API->>Q: Search with filter modality=image
    Q-->>API: top-k image chunks (with base64)
    API->>API: Assemble context + base64 images
    API->>GPT: Prompt + base64 images (vision)
    GPT-->>API: Answer with citations [1][2]
    API->>API: Build citation block with rendered images
    API-->>U: Answer + image citations rendered
```

---

## 9. Data Design

### 9.1 Entity Relationship Diagram (Relational DB)

```mermaid
erDiagram
    USER {
        uuid id PK
        string email
        string password_hash
        string google_id
        enum role
        bool is_verified
        timestamp created_at
    }

    DOCUMENT {
        uuid id PK
        string filename
        string original_filename
        enum file_type
        enum source_type
        enum status
        int total_chunks
        int completed_chunks
        string error_message
        uuid uploaded_by FK
        timestamp created_at
        timestamp completed_at
    }

    OTP {
        uuid id PK
        string otp_token
        string otp_code
        uuid user_id FK
        bool is_used
        timestamp expires_at
        timestamp created_at
    }

    USER ||--o{ DOCUMENT : "uploads"
    USER ||--o{ OTP : "receives"
```

---

### 9.2 Qdrant Chunk Schema (Vector DB Payload)

Every document chunk stored in Qdrant follows this payload structure:

```json
{
  "chunk_id":        "550e8400-e29b-41d4-a716-446655440000",
  "parent_chunk_id": "550e8400-e29b-41d4-a716-446655440001",
  "chunk_type":      "parent | child",
  "document_id":     "doc_uuid",
  "source_file":     "annual_report_2024.pdf",
  "source_type":     "document | web",
  "page_number":     7,
  "section_title":   "Revenue Analysis",
  "modality":        "text | table | image",
  "content":         "Raw text, markdown table, or VLM caption",
  "asset_base64":    "data:image/webp;base64,iVBORw0... (null for text/table)",
  "language":        "en",
  "created_at":      "2026-06-16T10:00:00Z"
}
```

**Qdrant Collection Config:**

```json
{
  "collection_name": "astrynox_chunks",
  "vectors": {
    "size": 1024,
    "distance": "Cosine"
  },
  "sparse_vectors": {
    "bm25": {}
  },
  "payload_schema": {
    "modality":   "keyword",
    "document_id": "keyword",
    "chunk_type": "keyword",
    "page_number": "integer"
  }
}
```

---

### 9.3 Redis Cache Schema

| Cache | Key Pattern | Value | TTL |
|-------|------------|-------|-----|
| L1 Answer Cache | `cache:answer:{md5(query)}` | JSON: `{answer, citations}` | 1 hour |
| L2 Embedding Cache | `cache:embed:{md5(query)}` | Binary: float32 vector (1024 dim) | 7 days |

**Cache invalidation on ingestion:**
```
Key pattern to flush: cache:answer:*
Command: FLUSHDB (dev) or SCAN + DEL with pattern (production)
```

---

### 9.4 Per-Chunk Metadata — Denormalized Design

Each chunk is fully self-contained. Section-level fields (`source_file`, `page_number`, `section_title`) are repeated across all child chunks from the same section — no joins required at retrieval time.

```mermaid
graph LR
    PARENT["sec_chunk_A\nsource_file: report.pdf\npage: 7\nsection: Revenue\nmodality: text"] 
    
    CHILD1["child_chunk_1\nsource_file: report.pdf ← copied\npage: 7 ← copied\nsection: Revenue ← copied\nmodality: text\ncontent: Revenue grew..."]

    CHILD2["child_chunk_img_1\nsource_file: report.pdf ← copied\npage: 7 ← copied\nsection: Revenue ← copied\nmodality: image\ncontent: Bar chart...\nasset_base64: webp..."]

    PARENT -.->|parent_chunk_id| CHILD1
    PARENT -.->|parent_chunk_id| CHILD2
```

---

## 10. Authentication Design

### 10.1 Email + Password Login with OTP

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js
    participant API as FastAPI
    participant DB as SQLite/Postgres
    participant RS as Resend

    U->>FE: Enter email + password
    FE->>API: POST /api/auth/login
    API->>DB: Verify email + password hash
    DB-->>API: User found + valid
    API->>API: Generate 6-digit OTP + temp token
    API->>DB: Store OTP (hashed, expires 10 min)
    API->>RS: Send OTP email via Resend
    RS-->>U: Email with OTP code
    API-->>FE: {otp_token, message: "OTP sent"}
    FE->>U: Show OTP input screen

    U->>FE: Enter OTP code
    FE->>API: POST /api/auth/verify-otp {otp_token, otp_code}
    API->>DB: Validate OTP (match + not expired + not used)
    DB-->>API: OTP valid
    API->>DB: Mark OTP as used
    API->>API: Issue JWT access + refresh tokens
    API-->>FE: {access_token, refresh_token, user}
    FE->>FE: Store tokens, redirect to /chat
```

---

### 10.2 Google OAuth2 Login (No OTP)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js
    participant API as FastAPI
    participant G as Google OAuth2
    participant DB as SQLite/Postgres

    U->>FE: Click "Login with Google"
    FE->>G: Redirect to Google consent screen
    G-->>U: Show consent screen
    U->>G: Grant consent
    G-->>FE: Redirect with auth code
    FE->>API: POST /api/auth/google {code}
    API->>G: Exchange code for tokens
    G-->>API: {id_token, user_info}
    API->>API: Verify id_token
    API->>DB: Find or create user by google_id
    DB-->>API: User record
    API->>API: Issue JWT access + refresh tokens
    API-->>FE: {access_token, refresh_token, user}
    FE->>FE: Store tokens, redirect to /chat
```

---

### 10.3 JWT Token Structure

```json
Access Token Payload:
{
  "sub": "user_uuid",
  "email": "user@company.com",
  "role": "employee | admin",
  "type": "access",
  "exp": 1750000000,
  "iat": 1749996400
}

Refresh Token Payload:
{
  "sub": "user_uuid",
  "type": "refresh",
  "exp": 1752000000,
  "iat": 1749996400
}
```

**Token lifetimes:**
- Access token: 15 minutes
- Refresh token: 7 days
- OTP: 10 minutes, single use

---

## 11. Security Design

### 11.1 Security Measures

| Layer | Measure |
|-------|---------|
| Passwords | Bcrypt hashing (cost factor 12) |
| JWT | HS256 signed with secret key, short-lived access tokens |
| OTP | 6-digit code, hashed in DB, 10-min expiry, single-use |
| Google OAuth2 | ID token verified server-side via Google public keys |
| API routes | JWT required on all endpoints except /auth/* |
| Admin routes | JWT + role check (`role == "admin"`) |
| File uploads | Validate MIME type + extension, max file size enforced |
| Input | Pydantic schema validation on all request bodies |
| Base64 images | Served only to authenticated users via API response |
| Qdrant | No public exposure — internal Docker network only |
| Redis | No public exposure — internal Docker network only |
| CORS | Whitelist frontend origin only |
| Rate limiting | Throttle /api/query (10 req/min per user) and /api/auth (5 req/min) |

### 11.2 Network Security (Production — AWS)

```mermaid
graph TB
    INTERNET[Internet] --> ALB[AWS ALB\nHTTPS only]
    ALB --> NGINX[Nginx\nSSL termination]
    NGINX --> FE[Next.js\nPort 3000]
    NGINX --> BE[FastAPI\nPort 8000]
    BE --> QDRANT[Qdrant\nPort 6333\nInternal only]
    BE --> REDIS[Redis\nPort 6379\nInternal only]
    BE --> S3[AWS S3\nPhase 2]
```

---

## 12. Error Handling

### 12.1 Ingestion Error Handling

| Error | Handling |
|-------|---------|
| Unsupported file type | Reject at upload, return 400 with message |
| Parse failure | Mark document `failed`, log error, continue other documents |
| VLM API failure | Retry 3x with exponential backoff, store chunk without caption if all fail |
| LLM API failure | Retry 3x, use raw text if all fail |
| Qdrant store failure | Retry 3x, mark document `failed` if all fail |
| Image optimization failure | Use original image bytes, attempt base64 encode |

### 12.2 Retrieval Error Handling

| Error | Handling |
|-------|---------|
| Cache connection failure | Bypass cache, continue to embedding |
| Embedding model failure | Return 500 with "Service temporarily unavailable" |
| Qdrant search failure | Return 500 with "Search service unavailable" |
| All chunks below threshold | Return "I don't have enough information" — no LLM call |
| LLM API failure | Return 500, do not cache |
| LLM returns no citations | Return answer without citations block |

### 12.3 HTTP Error Responses

```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type .exe is not supported. Allowed: pdf, docx, pptx, html, xlsx, csv",
    "status": 400
  }
}
```

---

## 13. Folder Structure

```
rag-pipeline/
│
├── app/                              # FastAPI backend
│   ├── main.py                       # App entry point, router registration
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py               # Auth endpoints
│   │   │   ├── documents.py          # Document upload/list/delete
│   │   │   ├── query.py              # Query endpoint
│   │   │   └── scraping.py           # Scraping trigger
│   │   └── dependencies.py           # JWT auth dependency, role check
│   │
│   ├── core/
│   │   ├── config.py                 # Env vars, settings (Pydantic BaseSettings)
│   │   ├── security.py               # JWT, bcrypt, OTP utilities
│   │   └── logging.py                # Structured logging setup
│   │
│   ├── services/
│   │   ├── ingestion/
│   │   │   ├── pipeline.py           # Orchestrates full ingestion flow
│   │   │   ├── parser.py             # Docling/Unstructured parsing, OCR
│   │   │   ├── chunker.py            # Chunking + parent-child tree builder
│   │   │   ├── image_optimizer.py    # Pillow resize → WebP → base64
│   │   │   ├── vlm.py                # GPT-4o VLM single call (classify + caption)
│   │   │   ├── embedder.py           # BGE dense + BM25 sparse embedding
│   │   │   └── storer.py             # Qdrant upsert
│   │   │
│   │   ├── retrieval/
│   │   │   ├── pipeline.py           # Orchestrates full retrieval flow
│   │   │   ├── cache.py              # Redis L1 + L2 read/write/invalidate
│   │   │   ├── embedder.py           # BGE dense + BM25 sparse for query
│   │   │   ├── searcher.py           # Qdrant ANN + BM25 parallel search
│   │   │   ├── fusion.py             # RRF merge + relevance threshold
│   │   │   └── assembler.py          # Context assembly + parent dedup + cite numbers
│   │   │
│   │   ├── generation/
│   │   │   ├── llm.py                # GPT-4o generation with citation prompt
│   │   │   └── citation_builder.py   # Build text/table/image citation blocks
│   │   │
│   │   ├── auth_service.py           # Login, OTP, Google OAuth2, JWT
│   │   └── scraper.py                # Playwright + BeautifulSoup scraping
│   │
│   ├── models/
│   │   ├── user.py                   # User SQLAlchemy model
│   │   ├── document.py               # Document SQLAlchemy model
│   │   └── otp.py                    # OTP SQLAlchemy model
│   │
│   └── schemas/
│       ├── auth.py                   # Pydantic request/response schemas for auth
│       ├── document.py               # Pydantic schemas for documents
│       ├── query.py                  # Pydantic schemas for query + citations
│       └── chunk.py                  # Pydantic schema for Qdrant chunk payload
│
├── frontend/                         # Next.js frontend
│   ├── app/
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── verify-otp/page.tsx
│   │   ├── chat/
│   │   │   └── page.tsx
│   │   └── admin/
│   │       ├── documents/page.tsx
│   │       └── scraping/page.tsx
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   └── MessageList.tsx
│   │   ├── citations/
│   │   │   ├── CitationBlock.tsx
│   │   │   ├── TextCitation.tsx
│   │   │   ├── TableCitation.tsx
│   │   │   └── ImageCitation.tsx
│   │   └── admin/
│   │       ├── DocumentList.tsx
│   │       ├── DocumentRow.tsx
│   │       ├── UploadForm.tsx
│   │       └── StatusBadge.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                    # Axios API client (base instance + interceptors)
│   │   ├── auth.ts                   # Token storage, refresh logic
│   │   ├── query-client.ts           # TanStack Query client config
│   │   └── types.ts                  # TypeScript types
│   │
│   ├── hooks/
│   │   ├── useDocuments.ts           # TanStack Query hooks — document list/upload/delete
│   │   └── useChat.ts                # TanStack Query mutation hook for queries
│   │
│   ├── tailwind.config.ts
│   ├── components.json               # shadcn/ui config
│   ├── next.config.ts
│   └── package.json
│
├── docs/
│   ├── PRD.md
│   ├── PROJECT_PLAN.md
│   └── SDD.md
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── .env.sample
├── .gitignore
└── requirements.txt
```

---

## 14. Environment Configuration

### 14.1 Environment Variables

```env
# App
APP_ENV=development
SECRET_KEY=your_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://astrynox:password@localhost:5432/astrynox-ai

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=astrynox_chunks

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Embedding (local)
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
EMBEDDING_DIMENSION=1024

# Resend (OTP)
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=noreply@astrynox.ai

# Google OAuth2
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 14.2 Docker Compose (Development)

```yaml
version: "3.9"
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    env_file: .env
    depends_on:
      - postgres
      - qdrant
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file: ./frontend/.env.local
    depends_on:
      - backend

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: astrynox
      POSTGRES_PASSWORD: password
      POSTGRES_DB: astrynox-ai
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

---

*Astrynox AI — SDD v1.0*
