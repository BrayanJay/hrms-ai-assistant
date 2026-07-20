# Astrynox AI

Enterprise internal knowledge assistant built on a Hybrid Multimodal RAG pipeline. Employees ask questions in natural language and receive cited answers grounded in company documents, with support for text, tables, and images.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+, async) |
| Frontend | Next.js 16 (App Router, TypeScript, Tailwind CSS v4, shadcn/ui) |
| Vector DB | Qdrant (self-hosted) |
| Relational DB | PostgreSQL 16 |
| Cache | Redis 7 (L1 answer · L2 embedding · L3 retrieval) |
| LLM / VLM | GPT-4o (OpenAI) |
| Embeddings | BAAI/bge-large-en-v1.5 (local, dense) + BM25 (sparse) |
| Document parsing | Docling |
| Auth | JWT + OTP email (Resend) + Google OAuth2 |
| Containerisation | Docker Compose |

---

## Architecture Overview

```
Upload → Docling parse → structure-aware chunk → BGE embed + BM25 index → Qdrant

Query  → GPT-4o rewrite → BGE embed (L2 cache) → hybrid search (L3 cache)
       → RRF fusion → cross-encoder rerank → parent-chunk assemble
       → GPT-4o generate (L1 cache) → inline citations → response
```

Conversation history is stored in Redis per session and passed to both the rewriter and the LLM so multi-turn references resolve correctly.

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop

---

## Local Setup

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd multimodel-rag

python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# or
.\venv\Scripts\Activate.ps1    # PowerShell

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.sample .env
```

Fill in `.env`:

```env
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">

OPENAI_API_KEY=sk-...

RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=noreply@yourdomain.com

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

NEXT_PUBLIC_API_URL=http://localhost:8000
```

The `DATABASE_URL`, `QDRANT_HOST`, and `REDIS_HOST` values are overridden by Docker Compose — you don't need to change them for local dev.

### 3. Start infrastructure services

```bash
docker compose up -d
```

This starts PostgreSQL (port 5433), Qdrant (6333), Redis (6379), and the FastAPI backend (8000).

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Services

| Service | URL |
|---|---|
| FastAPI (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| Qdrant dashboard | http://localhost:6333/dashboard |
| PostgreSQL | localhost:5433 (user: `astrynox`, db: `astrynox-ai`) |

---

## Key Routes

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register with email + password |
| POST | `/api/auth/login` | Login, returns OTP via email |
| POST | `/api/auth/verify-otp` | Verify OTP, returns JWT |
| GET | `/api/auth/google` | Google OAuth2 redirect |
| GET | `/api/auth/google/callback` | Google OAuth2 callback |

### Documents
| Method | Path | Description |
|---|---|---|
| POST | `/api/documents/upload` | Upload PDF (admin only) |
| GET | `/api/documents/` | List all documents |
| DELETE | `/api/documents/{id}` | Delete a document |

### Query
| Method | Path | Description |
|---|---|---|
| POST | `/api/query/` | Submit a query, returns answer + citations |
| POST | `/api/chat_session/` | Create a new chat session |

---

## Folder Structure

```
multimodel-rag/
├── app/                          # FastAPI backend
│   ├── main.py
│   ├── api/
│   │   ├── routes/               # auth, documents, query, chat_sessions, scraping
│   │   └── dependencies.py       # JWT auth dependency
│   ├── core/
│   │   ├── config.py             # Pydantic settings (env vars)
│   │   ├── security.py           # JWT, bcrypt, OTP
│   │   └── logging.py
│   ├── services/
│   │   ├── ingestion/            # pipeline, parser, chunker, embedder, vlm, storer
│   │   ├── retrieval/            # pipeline, cache, searcher, fusion, assembler, reranker
│   │   └── generation/           # llm, rewriter, citation_builder
│   ├── models/                   # SQLAlchemy models (user, document, otp, chat_session, query_events)
│   └── schemas/                  # Pydantic request/response schemas
│
├── frontend/                     # Next.js app
│   └── app/
│       ├── auth/                 # login, register, verify-otp
│       ├── chat/                 # main chat UI
│       └── (admin)/              # documents, qdrant, accuracy, configurations
│
├── alembic/                      # DB migrations
├── docs/                         # PRD, SDD, PROJECT_PLAN, LEARNING_GUIDE
├── docker-compose.yml
├── Dockerfile
├── .env.sample
└── requirements.txt
```

---

## Notes for New Developers

- **Re-ingesting a document** creates duplicate Qdrant points. Delete the existing document first, then re-upload.
- **BGE model** (~1.3 GB) downloads on first run. Subsequent runs use the local cache.
- **Admin routes** require a user with `is_admin=true` in the database. Set this directly in PostgreSQL for the first admin account.
- **Qdrant collection** is created automatically on first document ingest. Collection name is set via `QDRANT_COLLECTION` in `.env`.
- **L1 cache** (answer cache) is invalidated on every new document ingestion. L2 (embedding) and L3 (retrieval) expire on TTL.
