## Folder Structure

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