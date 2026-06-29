# Sprint 2 — Ingestion Pipeline
**Week 2 | Phase 1 MVP**

**Goal:** Full ingestion pipeline working — uploaded documents parsed, chunked, processed, embedded, and stored in Qdrant. Admin uploads a PDF with text, tables, and images and every chunk ends up in Qdrant with the correct tree structure.

---

## What you're building this week

Sprint 1 left the system at: admin uploads a file → DB record created with `status: "processing"` → nothing else happens.

Sprint 2 closes that loop. By Saturday, uploading a PDF should trigger a pipeline that:
1. Parses the file into 3 streams (text blocks / tables / images)
2. Groups elements into parent/child chunks with hierarchical IDs
3. Optimizes images to WebP base64
4. Runs VLM captioning on images, LLM summarization on long text
5. Embeds every chunk with BGE (dense) + BM25 (sparse)
6. Stores everything in Qdrant with full metadata
7. Updates document status to `"completed"` or `"failed"`

---

## Sprint 1 carry-overs to be aware of

These were deferred from Sprint 1 — keep them in mind but don't build them yet unless noted:

| Item | Deferral plan |
|------|--------------|
| Resend OTP on login inactivity | Sprint 2 auth polish day (if time) |
| Frontend protected routes / auth guard | Sprint 2 auth polish day |
| Backend `/auth/logout` endpoint | Sprint 2 auth polish day |

Add a **Sunday auth polish session** only if you finish Saturday early. Don't let it bleed into the pipeline work.

---

## Files to create this sprint

```
app/
  services/
    ingestion/
      parser.py        ← Docling + OCR fallback, 3-stream output
      chunker.py       ← Hierarchical chunking, parent/child IDs
      image_optimizer.py ← Resize → WebP → base64
      vlm.py           ← GPT-4o image classification + captioning
      embedder.py      ← BGE dense + BM25 sparse
      storer.py        ← Qdrant upsert
      pipeline.py      ← Orchestration: parse → chunk → concurrent tracks → embed → store
    scraper.py         ← Playwright + BeautifulSoup (Saturday)
```

The upload endpoint in `app/api/routes/documents.py` already creates the DB record. You'll trigger the pipeline from there (as a background task).

---

## Day-by-day plan

### Monday — Document Parsing (`parser.py`)

**What you're building:** A function that takes a file path, runs it through Docling, and returns three separate streams with positional metadata.

**Learn first (1 hr):**
- Docling GitHub README — especially how it returns `DoclingDocument` with blocks, tables, images
- Re-read `docs/LEARNING_GUIDE.md` Section 7

**Experiment (1 hr):**
```bash
# scratch/test_docling.py
# Parse a real PDF, print:
# - First 5 text blocks with page_number and y_position
# - First 2 table blocks as markdown
# - Image count and sizes
```
Use a PDF that has all three — a company report or slide deck works well.

**Build:**

`parser.py` must output this shape:
```python
{
    "text_blocks": [{"text": str, "page": int, "y_pos": float}, ...],
    "tables": [{"markdown": str, "page": int, "y_pos": float}, ...],
    "images": [{"bytes": bytes, "page": int, "y_pos": float}, ...]
}
```

Include Tesseract OCR as a fallback when Docling returns empty text (scanned PDFs).

**Test:**
- Parse 3 different PDFs: text-heavy, table-heavy, image-heavy
- Verify all 3 streams are populated with page numbers for each

---

### Tuesday — Chunking + Tree Building (`chunker.py`)

**What you're building:** Groups nearby elements into parent chunks (~1024 tokens), splits them into child chunks (~256 tokens), assigns stable IDs. Tables and images are atomic (one chunk each, no splitting).

**Learn first (1 hr):**
- Re-read `docs/LEARNING_GUIDE.md` Section 9 (hierarchical chunking) in full

**Experiment (1 hr):**
```bash
# scratch/test_chunker.py
# Feed raw text blocks, print tree:
# parent_id: "doc_uuid_p0"
#   child_id: "doc_uuid_p0_c0" → parent_chunk_id: "doc_uuid_p0"
#   child_id: "doc_uuid_p0_c1" → parent_chunk_id: "doc_uuid_p0"
```

**Build:**

Key constraint: **assign chunk_id and parent_chunk_id before any processing**. The embedder and storer need these IDs — don't generate them lazily.

Chunk shape:
```python
{
    "chunk_id": str,          # e.g. "{doc_id}_p{page}_c{n}"
    "parent_chunk_id": str | None,
    "type": "text" | "table" | "image",
    "content": str,           # text or markdown; empty for images
    "page": int,
    "image_bytes": bytes | None  # only for image chunks
}
```

**Test:**
- Print full chunk tree for a parsed PDF
- Verify every child has a `parent_chunk_id` that exists as a parent
- Verify image and table chunks have no children

---

### Wednesday — Image Optimization + Concurrent Tracks

**What you're building:** `image_optimizer.py` reduces images to ≤400KB WebP base64. `pipeline.py` splits Track 1 (text/table) and Track 2 (image) and runs them with `asyncio.gather()`.

**Learn first (1 hr):**
- Pillow `Image.save()` with `format="WebP"` and quality parameter
- `asyncio.gather()` — what it does and why it's needed here

**Experiment (1 hr):**
```bash
# scratch/test_optimizer.py
# Take a 2MB JPEG, optimize it, verify output < 400KB
# scratch/test_async.py
# Two async functions with different sleep times — verify they run concurrently
```

**Build:**

`image_optimizer.py`:
```python
async def optimize_image(image_bytes: bytes) -> str:
    # 1. Open with Pillow
    # 2. Resize to max 1280px on longest side (preserve aspect ratio)
    # 3. Convert to RGB (some images are RGBA)
    # 4. Save as WebP at quality=85
    # 5. If still > 400KB, reduce quality in a loop (80, 70, 60...)
    # 6. Return base64-encoded string with data:image/webp;base64, prefix
```

`pipeline.py` — the two tracks:
- **Track 1** (text + tables): optimize → embed → store → update status
- **Track 2** (images): optimize → VLM caption → embed → store
- `asyncio.gather(track_1_coroutine, track_2_coroutine)` runs both

**Test:**
- Verify a 2MB image comes out ≤400KB base64
- Verify Track 2 doesn't block Track 1 (time both independently then concurrently)
- Verify base64 string starts with `data:image/webp;base64,`

---

### Thursday — VLM Captioning + LLM Summarization (`vlm.py`)

**What you're building:** For each image chunk, call GPT-4o Vision to classify it and generate a caption. For text chunks over 500 words, generate an LLM summary.

**Learn first (1 hr):**
- OpenAI Vision API docs — how to pass `image_url` with base64 content
- Re-read `docs/LEARNING_GUIDE.md` Section 12

**Experiment (1 hr):**
```bash
# scratch/test_vlm.py
# Send a chart image to GPT-4o, verify JSON response:
# {"type": "chart", "caption": "Bar chart showing quarterly revenue..."}
# scratch/test_llm_summarize.py
# Summarize a 1000-word text chunk, verify output is condensed
```

**Build:**

`vlm.py` — one GPT-4o call per image:
```python
async def caption_image(base64_image: str) -> dict:
    # Returns {"type": "photo|chart|table|diagram|screenshot", "caption": str}
    # System prompt forces JSON output
    # Pass base64 via: {"type": "image_url", "image_url": {"url": base64_image}}
```

In `pipeline.py` — add to Track 1 for text:
```python
if word_count(chunk.content) > 500:
    chunk.summary = await llm_summarize(chunk.content)
```

For tables: extract markdown → if complex (>3 columns or >10 rows), add LLM summary.

**Test:**
- Run VLM on 5 image types: photo, chart, table screenshot, diagram, UI screenshot
- Verify correct `type` classification for each
- Run LLM summarization on a 1000-word chunk — verify output is shorter and coherent

---

### Friday — Embedding (`embedder.py`)

**What you're building:** BGE-large-en-v1.5 for dense vectors (1024-dim). BM25 for sparse vectors. Both used for every chunk.

**Learn first (1 hr):**
- BGE query prefix gotcha: document embedding uses no prefix, query embedding uses `"Represent this sentence: "` prefix. Get this wrong and retrieval quality collapses.
- rank-bm25 README

**Experiment (1 hr):**
```bash
# scratch/test_embed.py
# Embed one sentence, verify vector is shape (1024,)
# scratch/test_bm25.py
# Build a 5-doc BM25 index, query "revenue", verify matching docs ranked higher
```

**Build:**

`embedder.py` — two responsibilities:

1. BGE dense embedding:
```python
# Singleton pattern — load model once, reuse
_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    return _model

def embed_document(text: str) -> list[float]:
    # No prefix for documents
    return get_model().encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    # Batch for efficiency
    return get_model().encode(texts).tolist()
```

2. BM25 sparse:
```python
def build_bm25_tokens(text: str) -> list[str]:
    # Lowercase, tokenize, remove stopwords
    return text.lower().split()
```

The BM25 index itself is built in `storer.py` across all chunks in a document — `embedder.py` just tokenizes.

**Test:**
- Embed 10 chunks — verify all return length-1024 lists
- BM25 token search on a keyword — verify matching chunks ranked above non-matching

---

### Saturday — Qdrant Storage + Web Scraping

**What you're building:** `storer.py` upserts every chunk into Qdrant with dense + sparse vectors and full metadata payload. `scraper.py` scrapes a URL and feeds HTML into the same pipeline.

**Learn first (1 hr):**
- Qdrant quickstart — collection creation, upsert with `PointStruct`, sparse vector format
- Re-read `docs/LEARNING_GUIDE.md` Section 15

**Experiment (1 hr):**
```bash
# scratch/test_qdrant.py
# Create a collection with dense (1024-dim) + sparse vectors
# Upsert 3 chunks
# Search by vector, verify results returned with payload
```

**Build:**

`storer.py`:
```python
async def ensure_collection(client: QdrantClient) -> None:
    # Create "astrynox_chunks" collection if not exists
    # dense: VectorParams(size=1024, distance=Distance.COSINE)
    # sparse: SparseVectorParams()

async def store_chunk(client: QdrantClient, chunk: dict, dense_vector: list[float], bm25_tokens: list[str]) -> None:
    # Build sparse vector from BM25 term frequencies
    # Payload includes: chunk_id, parent_chunk_id, type, content, summary,
    #                   page, document_id, source_type, asset_base64 (for images)
    # Upsert as PointStruct
```

After all chunks are stored, update document status:
```python
document.status = "completed"
document.completed_at = datetime.now(timezone.utc)
# On any pipeline error: document.status = "failed", document.error_message = str(e)
```

Wire the pipeline into the upload endpoint as a FastAPI `BackgroundTask`:
```python
# In documents.py upload endpoint:
from fastapi import BackgroundTasks

@router.post("/upload")
async def upload_document(..., background_tasks: BackgroundTasks):
    # ... create DB record ...
    background_tasks.add_task(run_ingestion_pipeline, doc_id, file_bytes, db)
    return UploadResponse(...)
```

`scraper.py` — uses Playwright to render JavaScript-heavy pages, BeautifulSoup to extract text, then feeds into the same parser/chunker/pipeline flow.

**Test:**
- Upload a real PDF end-to-end → verify all chunks appear in Qdrant with correct payload fields
- Verify image chunks have `asset_base64` in payload
- Verify document status updates from `processing` → `completed`
- Trigger scrape on a URL → verify chunks created in Qdrant
- Upload a malformed file → verify status updates to `failed` with error message

---

## Sprint 2 Deliverables

- [ ] PDF with text + tables + images fully ingested end-to-end
- [ ] Concurrent tracks working (text stores early, images after optimization + VLM)
- [ ] Parent-child tree correctly stored in Qdrant with matching IDs
- [ ] Images stored as WebP base64 in Qdrant payload
- [ ] Web scraping ingests content from a URL
- [ ] Document status updates: `processing` → `completed` / `failed`

**Definition of Done:** Admin uploads a PDF with text, tables, and images — all chunks embedded and stored in Qdrant with the correct tree structure, WebP base64 images in payload, and document status showing `completed`.

---

## Key concepts to understand before you start

**Why concurrent tracks?**
VLM captioning is slow (1 API call per image). If you process images sequentially with text, a 50-page doc with 20 images blocks for several minutes. Track 1 finishes fast; Track 2 runs in parallel. User sees the text chunks searchable sooner.

**Why assign IDs before processing?**
The parent-child relationship must be consistent across the whole pipeline. If you generate chunk IDs lazily (during storage), you risk mismatches between what the embedder produces and what the storer saves. Assign all IDs in `chunker.py` upfront.

**Why BGE document embedding has no prefix?**
BGE uses a prefix (`"Represent this sentence: "`) only for query-time embedding. Document-time embedding uses the raw text. This is specific to the BAAI instruction-following models. Using the prefix on documents or omitting it on queries degrades cosine similarity and kills retrieval quality.

**Why BackgroundTasks not async directly in the route?**
The upload endpoint must return immediately — the client shouldn't wait 30 seconds for a PDF to fully ingest. FastAPI's `BackgroundTasks` runs after the response is sent. The client polls document status until it shows `completed`.

---

## Qdrant chunk payload schema (reference)

```python
{
    "chunk_id": "550e8400-e29b-41d4-p3_c1",
    "parent_chunk_id": "550e8400-e29b-41d4-p3",  # None for parent chunks
    "type": "text",           # "text" | "table" | "image"
    "content": str,           # raw text or table markdown
    "summary": str | None,    # LLM summary if content was long
    "page": int,
    "document_id": str,       # UUID from documents table
    "source_type": "document",  # or "web"
    "source_url": str | None,   # for scraped content
    "asset_base64": str | None  # data:image/webp;base64,... (images only)
}
```

---

## What's next (Sprint 3 preview)

Sprint 3 builds the retrieval pipeline that searches Qdrant using what you store this week:
- Redis cache L1 (answer) + L2 (embedding)
- Query embedding with the BGE query prefix
- Hybrid search: BGE dense + BM25 sparse, parallel
- RRF fusion + relevance threshold
- Context assembly with parent chunk deduplication

Getting the Qdrant payload shape right this week directly affects how easy Sprint 3 is. The `chunk_id`, `parent_chunk_id`, and `asset_base64` fields are load-bearing.
