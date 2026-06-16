# Project Plan
# Astrynox AI — 8-Week Individual Development Plan

**Version:** 1.0  
**Project Type:** Individual / Solo  
**Total Duration:** 8 Weeks  
**Phase 1 (MVP):** Week 1 – 4  
**Phase 2 (Enhanced):** Week 5 – 8  
**Budget:** Production infrastructure + API costs only  

---

## 1. Developer Resource

| Role | Person | Responsibility |
|------|--------|---------------|
| Full-Stack Developer | Brayan K. Jayawardhana | Everything — backend, frontend, pipeline, infra, testing |

**Estimated daily commitment:** 5–7 hours/day  
**Working days:** Monday – Saturday (6 days/week)  
**Total available hours:** ~240 hours across 8 weeks  

---

## 2. Budget Breakdown

### What costs nothing (free/local):
| Item | Why Free |
|------|---------|
| BAAI/bge-large-en-v1.5 embeddings | Local model, no API |
| Qdrant | Self-hosted via Docker |
| Redis | Self-hosted via Docker |
| Next.js / FastAPI | Open source |
| Docling / Unstructured | Open source |
| Tesseract OCR | Open source |
| Pillow image optimization | Open source |
| BM25 sparse retrieval | Open source |
| Development environment | Localhost |

---

### What costs money:

**OpenAI API (GPT-4o) — Ingestion (one-time per document set)**

| Operation | Estimate | Cost |
|-----------|---------|------|
| VLM captioning ~200 images (ingestion) | ~200 calls × 500 tokens | ~$0.50 |
| LLM summarization ~100 long chunks | ~100 calls × 800 tokens | ~$0.25 |
| **Ingestion total (one-time)** | | **~$1.00** |

**OpenAI API (GPT-4o) — Retrieval (per query, ongoing)**

| Usage Level | Queries/Month | Est. Cost/Month |
|------------|--------------|----------------|
| Light (dev/test) | ~500 queries | ~$2–5 |
| Moderate (internal use) | ~2,000 queries | ~$10–20 |
| Active (team daily use) | ~5,000 queries | ~$25–50 |

*Cache hits (L1) serve free — reduces API calls significantly.*

---

**Resend (OTP email)**

| Tier | Limit | Cost |
|------|-------|------|
| Free tier | 3,000 emails/month | $0 |
| Paid (if exceeded) | 50,000 emails/month | $20/month |

*Free tier is sufficient for MVP and early production.*

---

**AWS Production Infrastructure (Phase 2 onwards)**

| Service | Spec | Est. Cost/Month |
|---------|------|----------------|
| EC2 t3.medium (backend + Qdrant + Redis) | 2 vCPU, 4GB RAM | ~$30 |
| EC2 t3.small (Next.js frontend) | 1 vCPU, 2GB RAM | ~$15 |
| S3 (document + asset storage) | ~10GB | ~$0.25 |
| Data transfer | Minimal internal | ~$2 |
| **Total AWS/month** | | **~$47/month** |

*Alternative: Single EC2 t3.large (~$60/month) running everything via Docker Compose.*

---

**Total Cost Summary**

| Period | Cost |
|--------|------|
| Phase 1 (MVP, localhost) | ~$1–5 (API testing only) |
| Phase 2 launch (AWS + API) | ~$50–100/month |
| Ongoing production | ~$50–100/month |

---

## 3. Timeline Overview

```
Week 1  ████████  Sprint 1 — Foundation & Auth
Week 2  ████████  Sprint 2 — Ingestion Pipeline
Week 3  ████████  Sprint 3 — Retrieval Pipeline & Cache
Week 4  ████████  Sprint 4 — Generation, Citations & Polish
        ─────────────────────────────── Phase 1 Complete
Week 5  ████████  Sprint 5 — Retrieval Enhancements
Week 6  ████████  Sprint 6 — Conversation Memory & Analytics
Week 7  ████████  Sprint 7 — Production Migration (AWS)
Week 8  ████████  Sprint 8 — Multilingual + Final Polish
        ─────────────────────────────── Phase 2 Complete
```

---

## 4. Pre-Sprint: Environment Setup
**Complete this before Sprint 1 Day 1.**

---

### Step 1 — Install Core Tools

#### Python 3.11+
- [ ] Download from python.org/downloads — choose 3.11 or 3.12
- [ ] During install: check **"Add Python to PATH"**
- [ ] Verify:
```bash
python --version
# Expected: Python 3.11.x or 3.12.x
```

#### Node.js 20+
- [ ] Download LTS from nodejs.org
- [ ] Verify:
```bash
node --version   # Expected: v20.x.x or higher
npm --version    # Expected: 10.x.x or higher
```

#### Docker Desktop
- [ ] Download from docker.com/products/docker-desktop
- [ ] Install and start Docker Desktop
- [ ] Verify:
```bash
docker --version         # Expected: Docker version 27.x.x
docker-compose --version # Expected: Docker Compose version 2.x.x
```

#### Git
- [ ] Download from git-scm.com (includes Git Bash for Windows)
- [ ] Verify:
```bash
git --version  # Expected: git version 2.x.x
```

#### VS Code (recommended)
- [ ] Download from code.visualstudio.com
- [ ] Install extensions: Python, Pylance, ESLint, Tailwind CSS IntelliSense, Docker, GitLens

---

### Step 2 — Clone Repository & Create Folder Structure

```bash
# Navigate to your projects folder
cd /d/Dev/projects/rag-pipeline

# Create the scratch folder for experiments
mkdir scratch

# Create the services folder structure
mkdir -p app/api/routes
mkdir -p app/core
mkdir -p app/services/ingestion
mkdir -p app/services/retrieval
mkdir -p app/services/generation
mkdir -p app/models
mkdir -p app/schemas
mkdir -p docs
```

- [ ] Folder structure matches the SDD Section 13

---

### Step 3 — Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Git Bash)
source venv/Scripts/activate

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Verify venv is active (should show venv path)
which python
```

- [ ] `(venv)` prefix appears in terminal prompt

---

### Step 4 — Install Python Dependencies

```bash
# Make sure venv is active first
pip install -r requirements.txt
```

> **Note:** `torch` and `sentence-transformers` are large (~2GB). This will take 5–10 minutes on first install.

- [ ] All packages install without errors
- [ ] Verify key packages:
```bash
python -c "import fastapi; print(fastapi.__version__)"
python -c "import qdrant_client; print(qdrant_client.__version__)"
python -c "from sentence_transformers import SentenceTransformer; print('OK')"
```

---

### Step 5 — Install Playwright Browser

```bash
# Install Chromium browser for web scraping
playwright install chromium
```

- [ ] Chromium downloads successfully

---

### Step 6 — Create Next.js Frontend

```bash
# From the project root
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd frontend

# Initialize shadcn/ui
npx shadcn@latest init
# Choose: Default style, Slate base color, CSS variables: Yes

# Add core components
npx shadcn@latest add button input card badge textarea label

# Install TanStack Query and Axios
npm install @tanstack/react-query axios

# Install icons
npm install lucide-react
```

- [ ] `npm run dev` starts Next.js on `localhost:3000`
- [ ] shadcn `Button` component renders on test page

---

### Step 7 — Set Up API Keys & External Accounts

#### OpenAI
- [ ] Sign up at platform.openai.com
- [ ] Create API key under API Keys section
- [ ] Add billing method (required for GPT-4o)
- [ ] Set usage limit to $10/month during development

#### Resend (OTP Email)
- [ ] Sign up at resend.com
- [ ] Create an API key
- [ ] Add and verify your sending domain (or use the default `onboarding@resend.dev` for testing)

#### Google OAuth2
- [ ] Go to console.cloud.google.com
- [ ] Create a new project: "Astrynox AI"
- [ ] Enable "Google+ API" or "Google Identity"
- [ ] Go to Credentials → Create OAuth2 Client ID
- [ ] Application type: Web application
- [ ] Authorized redirect URIs: `http://localhost:3000/auth/google/callback`
- [ ] Copy Client ID and Client Secret

---

### Step 8 — Configure Environment Variables

```bash
# Copy the sample env file
cp .env.sample .env
```

Fill in `.env` with your actual values:

```env
# App
APP_ENV=development
SECRET_KEY=generate-a-long-random-string-here

# Database
DATABASE_URL=postgresql://astrynox:password@localhost:5432/astrynox-ai

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=astrynox_chunks

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# OpenAI
OPENAI_API_KEY=sk-...

# Resend
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=noreply@yourdomain.com

# Google OAuth2
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

- [ ] All values filled in `.env`
- [ ] `.env` is listed in `.gitignore` (never commit this file)

---

### Step 9 — Create .gitignore

```bash
# Create .gitignore at project root
```

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Environment
.env
.env.local
.env.*.local

# Scratch files
scratch/

# Node
frontend/node_modules/
frontend/.next/

# Docker volumes
postgres_data/
qdrant_data/
redis_data/

# IDE
.vscode/
.idea/
```

- [ ] `.env` and `venv/` confirmed in `.gitignore`

---

### Step 10 — Start Docker Services

```bash
# Start all services in background
docker-compose up -d

# Check all services are running
docker-compose ps
```

Expected output:
```
NAME                STATUS          PORTS
rag-pipeline-backend-1    running    0.0.0.0:8000->8000/tcp
rag-pipeline-frontend-1   running    0.0.0.0:3000->3000/tcp
rag-pipeline-postgres-1   running    0.0.0.0:5432->5432/tcp
rag-pipeline-qdrant-1     running    0.0.0.0:6333->6333/tcp
rag-pipeline-redis-1      running    0.0.0.0:6379->6379/tcp
```

- [ ] All 5 services show `running` status

---

### Step 11 — Initialize Database

```bash
# Initialize Alembic (only once)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "create initial tables"

# Apply migration
alembic upgrade head
```

- [ ] Migration runs without errors
- [ ] Connect to PostgreSQL and verify tables created:
```bash
docker exec -it rag-pipeline-postgres-1 psql -U astrynox -d astrynox-ai -c "\dt"
# Expected: users, documents, otp tables listed
```

---

### Step 12 — Verify Full Setup

Run each check — all should pass before starting Sprint 1:

```bash
# 1. FastAPI starts
uvicorn app.main:app --reload
# Visit: http://localhost:8000/docs — Swagger UI should appear

# 2. Next.js starts (in separate terminal)
cd frontend && npm run dev
# Visit: http://localhost:3000 — page should load

# 3. Qdrant accessible
curl http://localhost:6333/healthz
# Expected: {"title":"qdrant - Version x.x.x"}

# 4. Redis accessible
docker exec -it rag-pipeline-redis-1 redis-cli ping
# Expected: PONG

# 5. PostgreSQL accessible
docker exec -it rag-pipeline-postgres-1 pg_isready -U astrynox
# Expected: /var/run/postgresql:5432 - accepting connections

# 6. BGE model loads
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-large-en-v1.5'); print('BGE loaded OK')"
# Expected: BGE loaded OK (downloads model on first run ~1.3GB)
```

- [ ] FastAPI Swagger UI accessible at `localhost:8000/docs`
- [ ] Next.js accessible at `localhost:3000`
- [ ] Qdrant health check returns OK
- [ ] Redis responds to PING
- [ ] PostgreSQL accepting connections
- [ ] BGE model downloads and loads

---

### Step 13 — Create Scratch Folder & First Experiment

```bash
mkdir scratch
touch scratch/.gitkeep
```

Run your first experiment to confirm everything is wired:
```bash
# scratch/test_setup.py
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import redis

# Test embedding
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
vec = model.encode("Hello Astrynox AI")
print(f"Vector shape: {vec.shape}")  # (1024,)

# Test Qdrant
qd = QdrantClient(host="localhost", port=6333)
print(f"Qdrant collections: {qd.get_collections()}")

# Test Redis
r = redis.Redis(host="localhost", port=6379)
r.set("test", "ok")
print(f"Redis: {r.get('test')}")  # b'ok'

print("All systems go!")
```

```bash
python scratch/test_setup.py
# Expected: Vector shape: (1024,), Qdrant collections, Redis: b'ok', All systems go!
```

- [ ] `test_setup.py` runs without errors
- [ ] All systems confirmed working

---

### Environment Setup Complete ✓

```
✓ Python 3.11+ installed and venv active
✓ Node.js 20+ installed
✓ Docker Desktop running with all 5 services healthy
✓ Python dependencies installed (requirements.txt)
✓ Playwright Chromium installed
✓ Next.js + shadcn/ui + TanStack Query installed
✓ OpenAI, Resend, Google OAuth2 API keys configured
✓ .env file filled in and gitignored
✓ PostgreSQL tables created via Alembic
✓ BGE model downloaded and verified
✓ scratch/test_setup.py passes
```

**You are now ready to start Sprint 1.**

---

## 5. Phase 1 — MVP (Weeks 1–4)

> **Daily time allocation per step:**
> - **Learn** ~1 hr — read the resource, understand the concept
> - **Experiment** ~1 hr — run isolated examples in `scratch/`
> - **Develop** ~3–4 hrs — build the feature into Astrynox AI
> - **Test/Debug** ~1 hr — verify it works, fix issues before moving on

---

### Sprint 1 — Week 1: Foundation & Auth
**Goal:** Project scaffolding, Docker setup, authentication system, and admin upload UI running locally.

---

#### Monday — Project Setup & Docker

| Step | Tasks |
|------|-------|
| **Learn** | Read FastAPI Quick Start (fastapi.tiangolo.com/tutorial) — routing, app setup, CORS |
| **Experiment** | `scratch/test_fastapi.py` — one working route, run `uvicorn` and hit it in browser |
| **Develop** | Initialize FastAPI project structure, Next.js project, Docker Compose (FastAPI + PostgreSQL + Redis + Qdrant), folder structure from SDD, `.env` file |
| **Test/Debug** | `docker-compose up` — verify all 4 services start, FastAPI docs accessible at `localhost:8000/docs` |

#### Tuesday — Backend Auth (Email + JWT + OTP)

| Step | Tasks |
|------|-------|
| **Learn** | Read python-jose README + passlib docs (5 min each), re-read Section 4 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_jwt.py` — generate a token, decode it, verify expiry |
| **Develop** | User model + Alembic migration, `security.py` (hash_password, JWT, OTP utilities), register + login + verify-otp endpoints, Resend OTP email integration |
| **Test/Debug** | POST `/api/auth/register` → POST `/api/auth/login` → receive OTP in email → POST `/api/auth/verify-otp` → get JWT. Test with wrong OTP, expired OTP |

#### Wednesday — Google OAuth2

| Step | Tasks |
|------|-------|
| **Learn** | Read Google "Web Server" OAuth2 guide, re-read Section 5 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_google_oauth.py` — manually exchange an auth code and print userinfo |
| **Develop** | Google OAuth2 credentials in Google Cloud Console, `exchange_google_code()` service, `/api/auth/google` endpoint, find-or-create user by `google_id` |
| **Test/Debug** | Full Google login flow — click login → consent screen → redirect → JWT returned. Test with invalid code |

#### Thursday — Admin Document Upload API

| Step | Tasks |
|------|-------|
| **Learn** | Read FastAPI File Upload docs (5 min), re-read SQLAlchemy CRUD patterns from Section 2 |
| **Experiment** | `scratch/test_upload.py` — FastAPI endpoint that accepts a file and prints its name |
| **Develop** | Document model + migration, `/api/documents/upload` endpoint (validate MIME type, extract metadata, create DB record, set status: processing), `require_admin` dependency |
| **Test/Debug** | Upload a PDF as admin → verify record in PostgreSQL with status "processing". Test with non-admin JWT → expect 403. Test unsupported file type → expect 400 |

#### Friday — Frontend Auth Pages

| Step | Tasks |
|------|-------|
| **Learn** | Complete nextjs.org/learn interactive course (App Router section), re-read Section 18 of LEARNING_GUIDE |
| **Experiment** | `scratch/` Next.js page with a shadcn Button — verify Tailwind + shadcn rendering |
| **Develop** | Login page (email + password form), Register page, OTP verify page, Google login button, JWT storage in localStorage, `ProtectedRoute` component, Axios API client with auth interceptor |
| **Test/Debug** | Full login flow in browser — email login → OTP input → redirect to `/chat`. Google login → redirect to `/chat`. Invalid credentials → error message shown |

#### Saturday — Admin Dashboard UI

| Step | Tasks |
|------|-------|
| **Learn** | Re-read TanStack Query quick start (tanstack.com/query) — `useQuery` + `useMutation` |
| **Experiment** | `scratch/` — `useQuery` fetching a test API endpoint, render result in component |
| **Develop** | Admin dashboard page — document list (useDocuments hook), upload form (useUploadDocument mutation), status badge component (processing/completed/failed), delete document button |
| **Test/Debug** | Upload a file in UI → verify it appears in list with "processing" status. Delete a document → verify removed from list. Non-admin user cannot access `/admin` |

**Sprint 1 Deliverables:**
- [ ] Docker Compose running FastAPI + PostgreSQL + Redis + Qdrant locally
- [ ] Email/password login with OTP working end-to-end
- [ ] Google OAuth2 login working end-to-end
- [ ] Admin can upload a file and see it listed with "processing" status
- [ ] JWT auth protecting all API routes
- [ ] Admin-only routes return 403 for non-admin users

**Definition of Done:** User can register, log in via email (OTP) or Google, and admin can upload a document and see it listed.

---

### Sprint 2 — Week 2: Ingestion Pipeline
**Goal:** Full ingestion pipeline working — uploaded documents parsed, chunked, processed, embedded, and stored in Qdrant.

---

#### Monday — Document Parsing

| Step | Tasks |
|------|-------|
| **Learn** | Read Docling docs + GitHub README examples, re-read Section 7 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_docling.py` — parse a sample PDF, print text blocks with page numbers, print table markdown, print image count |
| **Develop** | `parser.py` — Docling integration, 3-stream separation (text blocks / tables / images) with page + y_position metadata, Tesseract OCR fallback for scanned docs |
| **Test/Debug** | Parse 3 different PDFs (text-heavy, table-heavy, image-heavy) — verify all 3 streams populated correctly with page numbers |

#### Tuesday — Chunking + Tree Building

| Step | Tasks |
|------|-------|
| **Learn** | Re-read Section 9 of LEARNING_GUIDE (hierarchical chunking) fully |
| **Experiment** | `scratch/test_chunker.py` — chunk a sample text into parent + children, print chunk_id + parent_chunk_id relationships |
| **Develop** | `chunker.py` — group elements by section via y_position proximity, assign chunk_id + parent_chunk_id upfront for ALL chunks, parent ~1024 tokens / children ~256 tokens, atomic chunks for tables and images |
| **Test/Debug** | Print full chunk tree for a parsed PDF — verify every child has correct parent_chunk_id, verify images and tables are atomic chunks pointing to correct parent |

#### Wednesday — Image Optimization + Concurrent Tracks

| Step | Tasks |
|------|-------|
| **Learn** | Read Pillow Image docs (resize + save as WebP), re-read asyncio section of LEARNING_GUIDE |
| **Experiment** | `scratch/test_optimizer.py` — optimize a 2MB JPEG, verify output is under 400KB WebP base64. `scratch/test_async.py` — two async tasks with `asyncio.gather()`, verify concurrent execution |
| **Develop** | `image_optimizer.py` — resize → WebP → iterative quality reduction → base64. `pipeline.py` — split chunks into Track 1 (text/table) and Track 2 (image), `asyncio.gather()` both tracks |
| **Test/Debug** | Time Track 1 and Track 2 separately vs concurrently — verify Track 2 doesn't block Track 1. Verify images over 400KB are reduced. Verify base64 string starts with `data:image/webp;base64,` |

#### Thursday — VLM Captioning + LLM Summarization

| Step | Tasks |
|------|-------|
| **Learn** | Read OpenAI Vision docs (platform.openai.com), re-read Section 12 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_vlm.py` — send a chart image to GPT-4o, verify JSON response with `type` and `caption`. `scratch/test_llm_summarize.py` — summarize a long text chunk |
| **Develop** | `vlm.py` — single GPT-4o call per image (classify + caption → JSON), `pipeline.py` — LLM summarization for text chunks over 500 words, table markdown extraction + LLM summary if complex |
| **Test/Debug** | Run VLM on 5 different image types (photo, chart, table, diagram, screenshot) — verify correct `type` classification. Run LLM summarization on a 1000-word chunk — verify condensed output |

#### Friday — Embedding (Dense + Sparse)

| Step | Tasks |
|------|-------|
| **Learn** | Read sbert.net quickstart + BGE query prefix gotcha from LEARNING_GUIDE Section 13. Read rank-bm25 README |
| **Experiment** | `scratch/test_embed.py` — embed a sentence with BGE, print vector shape (should be 1024). `scratch/test_bm25.py` — build a 5-doc BM25 index, query it, print ranked results |
| **Develop** | `embedder.py` (ingestion) — BGE-large-en-v1.5 singleton loader, `embed_document()` for chunks, `embed_batch()` for efficiency, BM25 tokenizer + index builder |
| **Test/Debug** | Embed 10 chunks — verify all return 1024-dim vectors. BM25 search for a keyword — verify matching chunks ranked higher |

#### Saturday — Qdrant Storage + Web Scraping

| Step | Tasks |
|------|-------|
| **Learn** | Read Qdrant quickstart (qdrant.tech/documentation/quickstart), re-read Section 15 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_qdrant.py` — create collection, upsert 3 chunks with dense + sparse vectors, search by vector, verify results returned with payload |
| **Develop** | `storer.py` — Qdrant collection setup, `store_chunk()` upsert with dense + sparse vectors + full metadata payload + base64. `scraper.py` — Playwright + BeautifulSoup scrape, feed HTML into ingestion pipeline. Document status → "completed" / "failed" |
| **Test/Debug** | Upload a real PDF end-to-end — verify all chunks appear in Qdrant with correct payload. Verify base64 is stored for image chunks. Trigger scrape on a URL — verify chunks created. Check document status updates correctly |

**Sprint 2 Deliverables:**
- [ ] PDF with text + tables + images fully ingested end-to-end
- [ ] Concurrent tracks working (text stores early, images after optimization + VLM)
- [ ] Parent-child tree correctly stored in Qdrant
- [ ] Images stored as base64 WebP in Qdrant payload
- [ ] Web scraping ingests company website content
- [ ] Document status updates: processing → completed / failed

**Definition of Done:** Admin uploads a PDF with text, tables, and images — all chunks embedded and stored in Qdrant with correct tree structure, base64 images in payload.

---

### Sprint 3 — Week 3: Retrieval Pipeline & Redis Cache
**Goal:** Full retrieval pipeline working — query embedded, hybrid search executed, results fused, filtered, and context assembled.

---

#### Monday — Redis Cache (L1 + L2)

| Step | Tasks |
|------|-------|
| **Learn** | Read redis-py README, re-read Section 16 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_redis.py` — set a key with TTL, get it, verify expiry after TTL. Test `invalidate_answer_cache()` — verify keys deleted |
| **Develop** | `cache.py` — L1 Answer Cache (set/get/invalidate, TTL 1hr), L2 Embedding Cache (set/get, TTL 7 days), `invalidate_answer_cache()` called on every new document ingestion |
| **Test/Debug** | Set an answer in L1 → retrieve it → verify exact match. Set embedding in L2 → retrieve → verify vector matches. Ingest a new document → verify L1 cache is flushed |

#### Tuesday — Query Embedding

| Step | Tasks |
|------|-------|
| **Learn** | Re-read BGE query prefix gotcha from LEARNING_GUIDE — query embedding vs document embedding |
| **Experiment** | `scratch/test_query_embed.py` — embed a query with prefix, embed a document without prefix, compute cosine similarity |
| **Develop** | `embedder.py` (retrieval) — `embed_query()` with BGE prefix, BM25 query tokenizer, query intake (clean + normalize + detect type: factual/visual/summary), L2 cache write after embedding |
| **Test/Debug** | Embed same query twice — second call should hit L2 cache (no model call). Verify query type detection: "show me the chart" → visual, "summarize" → summary, else → factual |

#### Wednesday — Hybrid Retrieval

| Step | Tasks |
|------|-------|
| **Learn** | Read Qdrant sparse vector search docs, re-read Section 15 hybrid search example |
| **Experiment** | `scratch/test_hybrid_search.py` — run dense search + sparse search in parallel on test collection, print both result sets |
| **Develop** | `searcher.py` — Qdrant ANN dense search, BM25 sparse search, `asyncio.gather()` both in parallel, visual query modality filter (`modality = "image"`) |
| **Test/Debug** | Run a factual query — verify both dense and sparse results returned. Run a visual query ("show me the chart") — verify only image chunks returned. Time parallel vs sequential search |

#### Thursday — RRF Fusion + Relevance Threshold

| Step | Tasks |
|------|-------|
| **Learn** | Re-read Section 17 of LEARNING_GUIDE (RRF formula), understand the k=60 constant |
| **Experiment** | `scratch/test_rrf.py` — create two ranked lists, apply RRF, print unified scores. Test threshold filtering |
| **Develop** | `fusion.py` — RRF merge (score = 1/(rank_dense+60) + 1/(rank_sparse+60)), sort by score descending, relevance threshold filter (discard below threshold), "not enough info" path when 0 chunks pass |
| **Test/Debug** | Query that should match → verify chunks pass threshold. Nonsense query ("asdfghjkl") → verify 0 chunks pass → "not enough information" returned. Tune threshold value with 5–10 test queries |

#### Friday — Context Assembly

| Step | Tasks |
|------|-------|
| **Learn** | Re-read assembler responsibilities from SDD Component Design section |
| **Experiment** | `scratch/test_assembler.py` — fetch chunks from Qdrant by ID, fetch parent, print assembled context |
| **Develop** | `assembler.py` — fetch full chunk payloads from Qdrant, fetch parent chunks for child results, deduplicate parents (one fetch per unique parent_chunk_id), load base64 from payload for image chunks, assign citation numbers [1][2][3] |
| **Test/Debug** | Retrieve chunks where 2 children share a parent — verify parent fetched only once. Verify image chunks have base64 loaded. Verify citation numbers assigned sequentially |

#### Saturday — Full Retrieval Integration Test

| Step | Tasks |
|------|-------|
| **Learn** | Review full retrieval pipeline flow from SDD Section 6.3 |
| **Experiment** | — |
| **Develop** | `pipeline.py` (retrieval) — wire all stages together: cache check → embed → search → fuse → threshold → assemble. Connect to `/api/query` route |
| **Test/Debug** | Run 10 test queries end-to-end (factual, visual, summary, nonsense). Verify cache hit on repeated query. Verify visual query returns image chunks with base64. Tune RRF threshold based on results |

**Sprint 3 Deliverables:**
- [ ] L1 and L2 Redis cache working correctly
- [ ] Hybrid retrieval returning relevant chunks
- [ ] RRF fusion producing correct unified ranking
- [ ] Relevance threshold filtering low-quality results
- [ ] Context assembly loading base64 images from Qdrant
- [ ] Parent chunk deduplication working

**Definition of Done:** Query runs through full retrieval pipeline — cache checked, hybrid search executed, results fused, filtered, context assembled correctly with images loaded from Qdrant.

---

### Sprint 4 — Week 4: Generation, Citations & End-to-End Polish
**Goal:** LLM generates cited answers, chat UI complete, full system tested and running end-to-end.

---

#### Monday — LLM Generation

| Step | Tasks |
|------|-------|
| **Learn** | Read OpenAI Chat Completions docs — system prompt, multi-turn, vision. Re-read Section 12 of LEARNING_GUIDE |
| **Experiment** | `scratch/test_generation.py` — send context + query to GPT-4o with citation prompt, verify [1][2][3] inline in response |
| **Develop** | `llm.py` — GPT-4o call with citation system prompt, pass base64 images for visual queries, write answer to L1 Answer Cache |
| **Test/Debug** | Test factual query → verify inline citations present. Test visual query → verify image passed to GPT-4o vision. Test query with no context → verify "not enough information" returned |

#### Tuesday — Citation Builder

| Step | Tasks |
|------|-------|
| **Learn** | Re-read citation builder design from SDD Section 6.1 Component table |
| **Experiment** | `scratch/test_citations.py` — build a text citation dict, a table citation dict, an image citation dict |
| **Develop** | `citation_builder.py` — parse LLM answer for [N] references, match to assembled chunks, build citation objects (text: source+snippet, table: source+markdown, image: source+base64) |
| **Test/Debug** | Verify [1][2][3] in answer match correct chunks. Verify image citation has base64. Verify table citation has markdown. Test answer with no citations → empty citations array |

#### Wednesday — Chat UI

| Step | Tasks |
|------|-------|
| **Learn** | Re-read TanStack Query `useMutation` pattern from Section 20 of LEARNING_GUIDE |
| **Experiment** | `scratch/` Next.js — `useMutation` calling a test endpoint, render result in component |
| **Develop** | Chat page — query input (ChatInput component), message list (ChatMessage component), `useChat` mutation hook, loading state ("Searching documents..."), inline [1][2][3] citation markers in answer text |
| **Test/Debug** | Submit a query → verify loading state shown → verify answer rendered with inline citations. Submit empty query → verify blocked. Network error → verify error message shown |

#### Thursday — Citation UI

| Step | Tasks |
|------|-------|
| **Learn** | Re-read ImageCitation + TableCitation components from LEARNING_GUIDE Section 19 |
| **Experiment** | `scratch/` — render a base64 image in Next.js `<img>` tag, render a markdown table with a library |
| **Develop** | CitationBlock component — TextCitation (source + snippet), TableCitation (rendered markdown table), ImageCitation (base64 `<img>` render), "not enough information" UI state (empty state component) |
| **Test/Debug** | Verify image renders correctly from base64. Verify table renders as HTML table not raw markdown. Verify citation numbers match inline [N] in answer. Test "not enough info" response shows empty state |

#### Friday — API Polish + Logging

| Step | Tasks |
|------|-------|
| **Learn** | Read Python `logging` docs (5 min) |
| **Experiment** | `scratch/test_logging.py` — structured log entry with timestamp, level, message |
| **Develop** | `logging.py` — structured logging setup, log per ingestion job (document_id, status, duration, error), log per query (query, cache_hit, response_time_ms), REST API response time header |
| **Test/Debug** | Upload a doc → verify ingestion log entries appear. Submit a query → verify query log with response time. Verify cache hit logged correctly |

#### Saturday — Full E2E Test + Docker Finalization

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | — |
| **Develop** | Docker Compose final config (health checks, restart policies, volume mounts), fix any cross-service issues found during testing |
| **Test/Debug** | Full E2E test sequence: (1) Register → login → get JWT. (2) Admin uploads a mixed PDF. (3) Wait for "completed" status. (4) Submit factual query → verify cited answer. (5) Submit visual query → verify image in citation. (6) Submit nonsense query → verify "not enough info". (7) Submit same query twice → verify cache hit (faster response). (8) Ingest new doc → verify L1 cache invalidated |

**Sprint 4 Deliverables:**
- [ ] GPT-4o generating cited answers with inline [1][2][3]
- [ ] Citation block showing text, table, and image citations
- [ ] Images rendered inline in citation block from base64
- [ ] Chat UI working end-to-end
- [ ] REST API endpoints working with logging
- [ ] Full system running via Docker Compose locally

**Definition of Done:** Employee logs in, asks a question, receives a cited answer with rendered visual citations in under 5 seconds. Admin uploads a document and it becomes queryable.

---

## 6. Phase 1 — Milestone Checklist

```
Week 1 ✓  Auth system (email/OTP + Google) + Admin upload UI
Week 2 ✓  Full ingestion pipeline (parse → chunk → embed → store)
Week 3 ✓  Full retrieval pipeline (cache → search → fuse → assemble)
Week 4 ✓  End-to-end system (generate → cite → UI → API)
           ↓
           Phase 1 MVP Complete
```

---

## 7. Phase 2 — Enhanced (Weeks 5–8)

---

### Sprint 5 — Week 5: Retrieval Enhancements
**Goal:** Improve retrieval quality with query rewriting, cross-encoder reranker, and L3 retrieval cache.

---

#### Monday — Query Rewriting (Learn + Build)

| Step | Tasks |
|------|-------|
| **Learn** | Read about query rewriting / HyDE pattern in RAG (search "query rewriting RAG") |
| **Experiment** | `scratch/test_query_rewrite.py` — send a vague query to GPT-4o with a rewrite prompt, compare embedding similarity before/after rewrite |
| **Develop** | `rewriter.py` — LLM-based query rewriter service, integrate into retrieval pipeline before embedding stage |
| **Test/Debug** | Test with 5 vague queries ("tell me about last year", "what happened with revenue") — verify rewritten queries are more specific and retrieve better chunks |

#### Tuesday — Query Rewriting (Tune + Cache Integration)

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | Compare retrieval quality: original query vs rewritten query on 10 test cases |
| **Develop** | Tune rewrite prompt for best results, update L1/L2 cache keys to use rewritten query, add rewrite step to retrieval pipeline |
| **Test/Debug** | Verify cache still works after rewriting — same query rewritten the same way should hit L2 cache |

#### Wednesday — Cross-Encoder Reranker (Learn + Build)

| Step | Tasks |
|------|-------|
| **Learn** | Read sentence-transformers cross-encoder docs (sbert.net/docs/cross_encoder/usage/usage.html) |
| **Experiment** | `scratch/test_reranker.py` — score (query, chunk) pairs with a cross-encoder, compare to RRF ranking |
| **Develop** | `reranker.py` — cross-encoder reranker after RRF fusion, re-score top-k chunks, return reranked list |
| **Test/Debug** | Compare top-5 results before and after reranker on 5 queries — verify reranker improves ordering |

#### Thursday — Cross-Encoder Reranker (Tune)

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | Benchmark latency with and without reranker — measure added time per query |
| **Develop** | Tune top-k passed to reranker (e.g. top-20 from RRF → reranker → top-5), integrate into retrieval pipeline |
| **Test/Debug** | Full retrieval pipeline with reranker — verify response time still under 5 seconds |

#### Friday — L3 Retrieval Cache

| Step | Tasks |
|------|-------|
| **Learn** | Re-read L3 cache design from SDD Phase 2 backlog section |
| **Experiment** | `scratch/test_l3_cache.py` — store chunk IDs in Redis keyed by embedding vector hash, retrieve on similar query |
| **Develop** | Add L3 Retrieval Cache to `cache.py` (key: hash of embedding vector, value: top-k chunk IDs, TTL: 30 min), integrate into retrieval pipeline between embedding and Qdrant search |
| **Test/Debug** | Submit same query twice — second call should hit L3 cache (skip Qdrant search). Verify chunk IDs match. Verify TTL expiry |

#### Saturday — Full Integration + Quality Comparison

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | — |
| **Develop** | Wire all 3 enhancements together: rewriter → embed → L3 cache → search → RRF → reranker → assemble |
| **Test/Debug** | Run same 10 test queries from Phase 1 — compare answer quality. Document any regressions. Tune thresholds if needed |

**Sprint 5 Deliverables:**
- [ ] Query rewriting working for vague queries
- [ ] Cross-encoder reranker improving top-k relevance
- [ ] L3 Retrieval Cache reducing Qdrant search calls
- [ ] Updated 3-layer Redis cache (Answer + Embedding + Retrieval)

---

### Sprint 6 — Week 6: Conversation Memory & Analytics Dashboard
**Goal:** Multi-turn conversation context and admin analytics visibility.

---

#### Monday — Conversation Memory (Backend)

| Step | Tasks |
|------|-------|
| **Learn** | Read about session-based conversation memory in RAG systems |
| **Experiment** | `scratch/test_memory.py` — store last 5 turns in Redis, retrieve and pass to GPT-4o, verify it references prior turns |
| **Develop** | Session model, conversation history stored in Redis (last N turns per session_id), pass history context to LLM generation |
| **Test/Debug** | Multi-turn test: Q1 "What is APAC revenue?" → Q2 "How does it compare to EMEA?" — verify Q2 resolves "it" correctly using history |

#### Tuesday — Conversation Memory (Query Rewriting)

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | `scratch/test_memory_rewrite.py` — rewrite a pronoun-heavy query using conversation history |
| **Develop** | Update `rewriter.py` to accept conversation history, resolve pronouns and references before embedding |
| **Test/Debug** | Test 5 multi-turn conversations — verify pronouns resolved, verify independent queries work normally (no history contamination) |

#### Wednesday — Analytics Backend

| Step | Tasks |
|------|-------|
| **Learn** | Read SQLAlchemy aggregation queries (count, avg, group_by) |
| **Experiment** | `scratch/test_analytics.py` — insert mock query events, run aggregate query for count + avg |
| **Develop** | Analytics event model (query, cache_hit, response_time_ms, timestamp), log event per query, aggregate endpoints (daily volume, cache hit rate, avg latency, top 10 queries) |
| **Test/Debug** | Submit 20 test queries → verify event count in DB. Verify cache hit rate calculates correctly. Verify avg latency is reasonable |

#### Thursday — Analytics API + Dashboard UI

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | `scratch/` — render a simple chart in Next.js using recharts or chart.js |
| **Develop** | Analytics API endpoints, admin analytics page — query volume chart (daily), cache hit rate, avg response time, top queries list |
| **Test/Debug** | Verify charts render with real data. Verify numbers match raw DB counts. Test empty state (no queries yet) |

#### Friday — Chat History UI

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | — |
| **Develop** | Show conversation history in chat UI — previous turns displayed, session persisted across page refresh |
| **Test/Debug** | Refresh page → verify conversation history persists. New session → verify history starts fresh |

#### Saturday — Polish + Integration

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | — |
| **Develop** | Final UI polish for conversation history, analytics dashboard responsive layout |
| **Test/Debug** | Full multi-turn conversation E2E test. Verify analytics dashboard updates in real time after queries |

**Sprint 6 Deliverables:**
- [ ] Multi-turn conversation working (references prior answers correctly)
- [ ] Admin analytics dashboard showing key metrics
- [ ] Cache hit rate and query volume visible to admin

---

### Sprint 7 — Week 7: Production Migration (AWS)
**Goal:** Deploy Astrynox AI to AWS, migrate asset storage to S3, production-grade config.

---

#### Monday — AWS Setup

| Step | Tasks |
|------|-------|
| **Learn** | Read AWS EC2 + S3 getting started guides (30 min) |
| **Experiment** | Create S3 bucket, upload a test file, generate pre-signed URL, verify access |
| **Develop** | EC2 instance (t3.medium), S3 bucket, VPC + security groups (ports 80, 443, 22), IAM role with S3 access, SSH key pair |
| **Test/Debug** | SSH into EC2, verify Docker is installable, verify S3 bucket accessible from EC2 |

#### Tuesday — S3 Migration (Ingestion)

| Step | Tasks |
|------|-------|
| **Learn** | Read boto3 S3 upload docs |
| **Experiment** | `scratch/test_s3.py` — upload a file to S3, get pre-signed URL, verify URL works |
| **Develop** | Update `image_optimizer.py` — after optimization, upload WebP to S3 instead of base64 encoding. Store `asset_path` (S3 key) in Qdrant payload instead of `asset_base64` |
| **Test/Debug** | Ingest a PDF with images → verify images uploaded to S3 → verify S3 key stored in Qdrant payload |

#### Wednesday — S3 Migration (Retrieval)

| Step | Tasks |
|------|-------|
| **Learn** | Read boto3 pre-signed URL docs |
| **Experiment** | Generate a pre-signed URL for an S3 object, verify it's accessible in browser for 1 hour |
| **Develop** | Update `assembler.py` — for image chunks, generate pre-signed S3 URL instead of returning base64. Update citation builder to use pre-signed URL in `<img>` src |
| **Test/Debug** | Submit a visual query → verify image citation renders from S3 pre-signed URL. Verify URL expires after TTL |

#### Thursday — Docker Production Config

| Step | Tasks |
|------|-------|
| **Learn** | Read Docker Compose production best practices (restart policies, health checks) |
| **Experiment** | Test `docker-compose.prod.yml` locally — verify health checks pass |
| **Develop** | `docker-compose.prod.yml` — production config (no volume mounts, env from AWS Secrets Manager or .env, health checks, restart: always), Nginx reverse proxy config |
| **Test/Debug** | Deploy to EC2 with `docker-compose.prod.yml` — verify all services start and pass health checks |

#### Friday — DNS + HTTPS

| Step | Tasks |
|------|-------|
| **Learn** | Read Certbot + Nginx SSL setup guide |
| **Experiment** | — |
| **Develop** | Nginx config (proxy to FastAPI + Next.js), Let's Encrypt SSL via Certbot, domain DNS pointing to EC2 |
| **Test/Debug** | Visit HTTPS URL → verify no SSL warnings. Verify HTTP redirects to HTTPS. Test API via HTTPS |

#### Saturday — Production Smoke Test

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | — |
| **Develop** | Fix any issues found during smoke test |
| **Test/Debug** | Full E2E on production AWS: register → login → upload doc → ingest → query → cited answer with S3 images. Monitor CloudWatch logs. Verify response times under load |

**Sprint 7 Deliverables:**
- [ ] Full system running on AWS EC2
- [ ] Images/assets stored in S3, retrieved via pre-signed URLs
- [ ] HTTPS enabled with valid certificate
- [ ] Production environment variables configured securely

---

### Sprint 8 — Week 8: Multilingual Support + Final Polish
**Goal:** Sinhala and Tamil query support, final UI polish, and production hardening.

---

#### Monday — Language Detection

| Step | Tasks |
|------|-------|
| **Learn** | Read fasttext / langdetect docs |
| **Experiment** | `scratch/test_langdetect.py` — detect language of 10 sample queries in English, Sinhala, Tamil |
| **Develop** | Language detection in query intake, tag query with `lang_code` (en/si/ta), pass to downstream services |
| **Test/Debug** | Test detection accuracy on 20 queries (English, Sinhala, Tamil) — verify correct language detected |

#### Tuesday — Multilingual Embedding (LaBSE)

| Step | Tasks |
|------|-------|
| **Learn** | Read LaBSE model card on Hugging Face (sentence-transformers/LaBSE) |
| **Experiment** | `scratch/test_labse.py` — embed an English sentence and its Sinhala translation, compute cosine similarity — should be high |
| **Develop** | Swap BGE → LaBSE in embedder, re-embed all existing chunks (background job), update Qdrant collection dimension if needed |
| **Test/Debug** | Verify Sinhala query retrieves English document chunks correctly (cross-lingual retrieval) |

#### Wednesday — Multilingual Retrieval

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | `scratch/test_multilingual_retrieval.py` — translate a Sinhala query to English, run BM25 on English index, compare results |
| **Develop** | Translate non-English queries to English for BM25 sparse search (GPT-4o translation), LaBSE handles dense cross-lingual retrieval natively |
| **Test/Debug** | Sinhala query about company policy → verify relevant English chunks retrieved |

#### Thursday — Multilingual Generation

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | `scratch/test_multilingual_gen.py` — ask GPT-4o to respond in Sinhala, verify output language |
| **Develop** | Pass `detected_language` to LLM system prompt ("Respond in Sinhala"), test full pipeline Sinhala/Tamil queries → answers in same language |
| **Test/Debug** | 10 Sinhala queries → verify answers in Sinhala. 10 Tamil queries → verify answers in Tamil. English queries → unaffected |

#### Friday — UI Polish

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | Test UI on mobile viewport in Chrome DevTools |
| **Develop** | Mobile responsive layout (chat + admin), loading skeletons, error states, empty states, better typography and spacing |
| **Test/Debug** | Test on mobile viewport (375px, 768px), verify all pages usable on small screens |

#### Saturday — Final Production Hardening

| Step | Tasks |
|------|-------|
| **Learn** | — |
| **Experiment** | — |
| **Develop** | Rate limiting (slowapi: 10 req/min for query, 5 req/min for auth), input sanitization (strip HTML, max length), final error handling review |
| **Test/Debug** | Final E2E test on production — all query types, all languages, cache behaviour, S3 images, mobile UI. Stress test rate limiter |

**Sprint 8 Deliverables:**
- [ ] Sinhala and Tamil queries returning correct answers in the same language
- [ ] Cross-lingual retrieval working (Sinhala query → English document → Sinhala answer)
- [ ] UI polished and mobile responsive
- [ ] Rate limiting and input validation in place

---

## 8. Phase 2 — Milestone Checklist

```
Week 5 ✓  Retrieval enhancements (query rewriting + reranker + L3 cache)
Week 6 ✓  Conversation memory + admin analytics dashboard
Week 7 ✓  AWS production deployment + S3 asset migration
Week 8 ✓  Multilingual support (Sinhala + Tamil) + final polish
           ↓
           Phase 2 Complete — Production Ready
```

---

## 9. Full 8-Week Timeline

| Week | Phase | Sprint | Key Deliverable |
|------|-------|--------|----------------|
| 1 | 1 | Sprint 1 | Auth system + admin upload UI |
| 2 | 1 | Sprint 2 | Ingestion pipeline end-to-end |
| 3 | 1 | Sprint 3 | Retrieval pipeline + Redis cache |
| 4 | 1 | Sprint 4 | LLM generation + citations + chat UI |
| — | — | — | **Phase 1 MVP Complete** |
| 5 | 2 | Sprint 5 | Query rewriting + reranker + L3 cache |
| 6 | 2 | Sprint 6 | Conversation memory + analytics |
| 7 | 2 | Sprint 7 | AWS deployment + S3 migration |
| 8 | 2 | Sprint 8 | Multilingual + final polish |
| — | — | — | **Phase 2 Production Ready** |

---

## 10. Risks — Solo Developer Specific

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Blocked on a single task with no team to unblock | High | High | Set 4-hour time-box per task — if stuck, move on and revisit |
| Scope creep within a sprint | High | Medium | Strictly follow sprint task list, log new ideas to backlog |
| Underestimating ingestion pipeline complexity | Medium | High | Build ingestion pipeline incrementally — text first, then tables, then images |
| API costs higher than expected during dev/testing | Medium | Low | Use small test document set (5–10 docs) during Sprint 2–3, full set only in Sprint 4 |
| AWS setup taking longer than 1 day | Medium | Medium | Prepare AWS account and IAM roles before Sprint 7 starts |
| LaBSE re-embedding in Sprint 8 slow on CPU | Medium | Medium | Schedule re-embedding as background job overnight |
| BGE local model slow on CPU for large batches | Low | Medium | Batch embedding calls, run ingestion async |
| 4-week Phase 1 timeline slips | Medium | High | Cut web scraping and move to Phase 2 Sprint 5 if behind |

---

## 11. Environment Setup Checklist (Summary)

**Local Dev (before Sprint 1 Day 1):**
- [ ] Python 3.11+ with venv
- [ ] Node.js 20+ and npm
- [ ] Docker Desktop installed
- [ ] Git repository initialized
- [ ] OpenAI API key obtained
- [ ] Resend account created + API key
- [ ] Google OAuth2 credentials created (Google Cloud Console)
- [ ] `.env` file configured with all keys

**Docker Compose services (Sprint 1):**
- [ ] FastAPI (backend)
- [ ] Next.js (frontend)
- [ ] Qdrant (vector DB)
- [ ] Redis (cache)

**AWS (before Sprint 7):**
- [ ] AWS account active
- [ ] IAM user with EC2 + S3 permissions
- [ ] S3 bucket created
- [ ] EC2 instance type decided (t3.medium recommended)
- [ ] Domain name purchased (optional)

---

## 12. Definition of Done — Project Level

A feature is done when:
- Works end-to-end in the target environment (local for Phase 1, AWS for Phase 2)
- No breaking changes to existing features
- Basic error handling covers failure paths
- Tested manually with real documents

A sprint is done when:
- All sprint tasks are completed
- The sprint deliverables listed above are verified
- No critical bugs in previously completed features

---

*Astrynox AI — Project Plan v1.0 | Individual Development | 8-Week Schedule*
