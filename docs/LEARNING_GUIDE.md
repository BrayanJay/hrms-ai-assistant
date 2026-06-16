# Learning Guide
# Astrynox AI — Technologies & Coding Examples

**Purpose:** A self-study guide covering every technology used in Astrynox AI, ordered by sprint so you learn what you need right before you build it.

---

## Table of Contents

1. [FastAPI](#1-fastapi)
2. [PostgreSQL + SQLAlchemy + Alembic](#2-postgresql--sqlalchemy--alembic)
3. [Pydantic](#3-pydantic)
4. [JWT Authentication](#4-jwt-authentication)
5. [Google OAuth2](#5-google-oauth2)
6. [Resend — OTP Email](#6-resend--otp-email)
7. [Docling — Document Parsing](#7-docling--document-parsing)
8. [Tesseract OCR](#8-tesseract-ocr)
9. [Hierarchical Chunking](#9-hierarchical-chunking)
10. [Pillow — Image Optimization](#10-pillow--image-optimization)
11. [asyncio — Concurrent Programming](#11-asyncio--concurrent-programming)
12. [OpenAI API — VLM + LLM](#12-openai-api--vlm--llm)
13. [sentence-transformers — BGE Local Embedding](#13-sentence-transformers--bge-local-embedding)
14. [BM25 — Sparse Embedding](#14-bm25--sparse-embedding)
15. [Qdrant — Vector Database](#15-qdrant--vector-database)
16. [Redis — Caching](#16-redis--caching)
17. [RRF Fusion](#17-rrf-fusion)
18. [Next.js App Router](#18-nextjs-app-router)
19. [Tailwind CSS + shadcn/ui](#19-tailwind-css--shadcnui)
20. [TanStack Query](#20-tanstack-query)

---

## How to Learn Fast

### The Core Loop (repeat for every technology)
```
1. Read the quick start only       (~20 min)
2. Run the code example            (~10 min)
3. Break it and fix it             (~20 min)
4. Plug it into Astrynox AI        (rest of the day)
```
One technology per day. Never read full docs — go straight to Quick Start or Tutorial.

---

### Best Resource Per Technology

| Technology | Resource | Est. Time |
|-----------|---------|----------|
| FastAPI | fastapi.tiangolo.com/tutorial — Quick Start + Routing + Dependencies | 1 day |
| SQLAlchemy async | SQLAlchemy 2.0 docs — "ORM Quickstart" section only | half day |
| Alembic | alembic.sqlalchemy.org — "Tutorial" page only | 2 hours |
| Pydantic | pydantic.dev/concepts — "Models" section only | 2 hours |
| JWT | python-jose README + Section 4 of this guide | 2 hours |
| Google OAuth2 | Google "Web Server" OAuth2 guide | 2 hours |
| Resend | resend.com/docs — Python section | 30 min |
| Docling | docling.dev docs + GitHub README examples | half day |
| Tesseract | pytesseract GitHub README | 1 hour |
| asyncio | realpython.com/async-io-python | 1 day |
| OpenAI API | platform.openai.com/docs — Vision + Chat sections | half day |
| sentence-transformers | sbert.net/docs/quickstart — Usage section only | 2 hours |
| BM25 | rank-bm25 GitHub README | 1 hour |
| Qdrant | qdrant.tech/documentation/quickstart | half day |
| Redis | redis-py GitHub README | 2 hours |
| Pillow | pillow.readthedocs.io — Image class section only | 2 hours |
| Next.js App Router | nextjs.org/learn — official interactive course | 1 day |
| Tailwind CSS | tailwindcss.com/docs — Core Concepts section only | half day |
| shadcn/ui | ui.shadcn.com/docs — Introduction + use component docs as reference | 1 hour |
| TanStack Query | tanstack.com/query/latest/docs/framework/react/quick-start | half day |

---

### 3 Rules That Save the Most Time

**Rule 1 — Never read the full docs**
Go straight to Quick Start or Tutorial. Read just enough to get one thing working. Look up the rest when you need it.

**Rule 2 — Use Claude as your tutor**
When you hit something confusing, paste the code and ask:
- *"Why does this fail?"*
- *"What's the simplest way to do X in FastAPI?"*
- *"Show me a real example of Qdrant hybrid search"*

**Rule 3 — Build isolated experiments first**
Before wiring into the real pipeline, test in a scratch file:
```bash
# create a scratch folder for experiments
mkdir scratch
```
```python
# scratch/test_qdrant.py — test before touching the real code
from qdrant_client import QdrantClient
# try things here, break things here
```
Once it works in isolation, copy the pattern into Astrynox AI.

---

### Suggested Daily Schedule

```
Morning  (2 hrs) — Read the resource for today's technology
                   Run the code example from this guide in scratch/
Afternoon (4 hrs) — Build that technology into Astrynox AI
                    Test it end-to-end before moving on
```

---

### What to Skip for MVP (learn later if needed)

| Topic | Why Skip Now |
|-------|-------------|
| SQLAlchemy relationships / eager loading | Simple queries are enough for MVP |
| Next.js server components | Use `"use client"` on everything for now |
| asyncio internals | Just use `gather()` and `to_thread()` from this guide |
| Qdrant advanced indexing | Default settings work fine at 100 documents |
| Torch GPU setup | CPU inference is fine for BGE at MVP scale |

---

## 1. FastAPI

**What it is:** Python async web framework for building REST APIs — fast, type-safe, auto-documented.

**Key concepts:** routing, dependency injection, async handlers, middleware, background tasks

---

### Basic App Setup
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, documents, query, scraping

app = FastAPI(title="Astrynox AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(query.router,     prefix="/api/query",     tags=["query"])
app.include_router(scraping.router,  prefix="/api/scraping",  tags=["scraping"])
```

---

### Route + Dependency Injection
```python
# app/api/routes/documents.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),  # injected dependency
):
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats..."]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()
    # trigger ingestion pipeline
    return {"filename": file.filename, "status": "processing"}
```

---

### Dependency: JWT Auth Guard
```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.models.user import User

bearer = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

---

### Background Tasks (for ingestion)
```python
from fastapi import BackgroundTasks

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(require_admin),
):
    contents = await file.read()
    document = await create_document_record(file.filename)

    # runs after response is sent — don't block the request
    background_tasks.add_task(run_ingestion_pipeline, document.id, contents)

    return {"document_id": document.id, "status": "processing"}
```

> **Gotcha:** `BackgroundTasks` runs in the same process — fine for MVP. For production use Celery or ARQ.

---

## 2. PostgreSQL + SQLAlchemy + Alembic

**What it is:** PostgreSQL is the relational DB. SQLAlchemy is the Python ORM. Alembic handles schema migrations.

**Key concepts:** async sessions, declarative models, relationships, migrations

---

### Async Database Setup
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

### User Model
```python
# app/models/user.py
import uuid
from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email:         Mapped[str]        = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id:     Mapped[str | None] = mapped_column(String(255), nullable=True)
    role:          Mapped[str]        = mapped_column(String(20), default="employee")
    is_verified:   Mapped[bool]       = mapped_column(Boolean, default=False)
    created_at:    Mapped[datetime]   = mapped_column(default=lambda: datetime.now(timezone.utc))
```

---

### Document Model
```python
# app/models/document.py
import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id:               Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename:         Mapped[str]         = mapped_column(String(255), nullable=False)
    file_type:        Mapped[str]         = mapped_column(String(20), nullable=False)
    source_type:      Mapped[str]         = mapped_column(String(20), default="document")
    status:           Mapped[str]         = mapped_column(String(20), default="processing")
    total_chunks:     Mapped[int]         = mapped_column(Integer, default=0)
    completed_chunks: Mapped[int]         = mapped_column(Integer, default=0)
    error_message:    Mapped[str | None]  = mapped_column(String(500), nullable=True)
    uploaded_by:      Mapped[uuid.UUID]   = mapped_column(ForeignKey("users.id"))
    created_at:       Mapped[datetime]    = mapped_column(default=lambda: datetime.now(timezone.utc))
    completed_at:     Mapped[datetime | None] = mapped_column(nullable=True)
```

---

### CRUD with Async Session
```python
# app/services/document_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document

async def get_all_documents(db: AsyncSession) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

async def update_document_status(db: AsyncSession, doc_id: str, status: str):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc:
        doc.status = status
        await db.commit()
```

---

### Alembic Migrations
```bash
# Initialize Alembic
alembic init alembic

# Create a migration after changing models
alembic revision --autogenerate -m "create users and documents tables"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

```python
# alembic/env.py — point to your models
from app.core.database import Base
from app.models import user, document, otp   # import all models so Alembic sees them

target_metadata = Base.metadata
```

> **Gotcha:** Use `asyncpg` driver for async SQLAlchemy (`postgresql+asyncpg://`). The sync `psycopg2` driver will block your event loop.

---

## 3. Pydantic

**What it is:** Data validation and serialization library — used for all FastAPI request/response schemas.

**Key concepts:** BaseModel, Field, validators, nested models

---

### Request + Response Schemas
```python
# app/schemas/query.py
from pydantic import BaseModel, Field
from typing import Literal

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    query_type: Literal["factual", "visual", "summary"] = "factual"

class CitationSchema(BaseModel):
    id: int
    source_file: str
    page_number: int
    section_title: str
    modality: Literal["text", "table", "image"]
    content: str
    asset_base64: str | None = None

class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationSchema]
    from_cache: bool
    response_time_ms: int
```

---

### Settings with Pydantic BaseSettings
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "astrynox_chunks"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"

    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_DIMENSION: int = 1024

    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 4. JWT Authentication

**What it is:** JSON Web Tokens — signed tokens used to authenticate API requests.

**Key concepts:** access token, refresh token, signing, decoding, expiry

---

### JWT Utilities
```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str, email: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None
```

---

### OTP Generation + Verification
```python
# app/core/security.py (continued)
import secrets
import hashlib

def generate_otp() -> tuple[str, str]:
    """Returns (plain_otp, hashed_otp)"""
    otp = str(secrets.randbelow(900000) + 100000)  # 6-digit
    hashed = hashlib.sha256(otp.encode()).hexdigest()
    return otp, hashed

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    return hashlib.sha256(plain_otp.encode()).hexdigest() == hashed_otp
```

---

## 5. Google OAuth2

**What it is:** Login via Google account — exchanges an auth code for user identity without handling passwords.

**Key concepts:** authorization URL, code exchange, ID token verification

---

### Google OAuth2 Flow
```python
# app/services/auth_service.py
import httpx
from app.core.config import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

async def exchange_google_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        tokens = token_response.json()

        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        return userinfo_response.json()
        # Returns: {id, email, name, picture}
```

```python
# app/api/routes/auth.py
@router.post("/google")
async def google_login(code: str, db: AsyncSession = Depends(get_db)):
    userinfo = await exchange_google_code(code)

    user = await get_user_by_google_id(db, userinfo["id"])
    if not user:
        user = await create_user_google(db, userinfo["id"], userinfo["email"])

    access_token  = create_access_token(str(user.id), user.email, user.role)
    refresh_token = create_refresh_token(str(user.id))

    return {"access_token": access_token, "refresh_token": refresh_token}
```

> **Gotcha:** Never trust the `code` from the frontend without server-side exchange. Always verify tokens server-side.

---

## 6. Resend — OTP Email

**What it is:** Email API service for sending transactional emails — used for OTP delivery.

---

### Send OTP Email
```python
# app/services/auth_service.py
import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

async def send_otp_email(email: str, otp_code: str):
    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": email,
        "subject": "Your Astrynox AI Login Code",
        "html": f"""
            <h2>Your login code</h2>
            <p>Enter this code to complete your login:</p>
            <h1 style="letter-spacing: 8px; font-size: 36px;">{otp_code}</h1>
            <p>This code expires in 10 minutes.</p>
            <p>If you didn't request this, ignore this email.</p>
        """
    })
```

---

### Full Login Flow
```python
@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    plain_otp, hashed_otp = generate_otp()
    otp_token = create_otp_token(str(user.id))  # short-lived JWT for OTP session

    await store_otp(db, user.id, hashed_otp, expires_minutes=10)
    await send_otp_email(user.email, plain_otp)

    return {"otp_token": otp_token, "message": "OTP sent to your email"}
```

---

## 7. Docling — Document Parsing

**What it is:** IBM's document parsing library — extracts structured content (text, tables, images) from PDF, DOCX, PPTX, HTML.

**Key concepts:** DocumentConverter, DoclingDocument, table extraction, image extraction with position

---

### Install
```bash
pip install docling
```

---

### Parse a PDF
```python
# app/services/ingestion/parser.py
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from pathlib import Path

converter = DocumentConverter()

def parse_document(file_path: str) -> dict:
    result = converter.convert(file_path)
    doc = result.document

    text_blocks = []
    tables = []
    images = []

    # Extract text blocks with position
    for item, level in doc.iterate_items():
        if hasattr(item, "text") and item.text:
            text_blocks.append({
                "text": item.text,
                "page": getattr(item.prov[0], "page_no", 1) if item.prov else 1,
                "section": getattr(item, "label", ""),
                "y_pos": getattr(item.prov[0], "bbox", {}).get("t", 0) if item.prov else 0,
            })

    # Extract tables
    for table in doc.tables:
        tables.append({
            "markdown": table.export_to_markdown(),
            "page": table.prov[0].page_no if table.prov else 1,
            "y_pos": table.prov[0].bbox.t if table.prov else 0,
        })

    # Extract images
    for picture in doc.pictures:
        images.append({
            "image_bytes": picture.get_image(doc).tobytes() if picture.get_image(doc) else None,
            "page": picture.prov[0].page_no if picture.prov else 1,
            "y_pos": picture.prov[0].bbox.t if picture.prov else 0,
        })

    return {
        "text_blocks": text_blocks,
        "tables": tables,
        "images": images,
        "metadata": {
            "filename": Path(file_path).name,
            "total_pages": len(doc.pages),
        }
    }
```

> **Gotcha:** Docling requires `poppler` for PDF rendering on Windows. Install via `conda install -c conda-forge poppler` or download binaries.

---

## 8. Tesseract OCR

**What it is:** Open-source OCR engine — extracts text from scanned/image-based documents.

---

### Install
```bash
pip install pytesseract pillow
# Also install Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki
```

---

### OCR on a Scanned PDF
```python
# app/services/ingestion/parser.py
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io

def ocr_scanned_pdf(file_bytes: bytes) -> list[dict]:
    pages = convert_from_bytes(file_bytes, dpi=300)
    text_blocks = []

    for page_num, page_image in enumerate(pages, start=1):
        text = pytesseract.image_to_string(page_image, lang="eng")
        if text.strip():
            text_blocks.append({
                "text": text.strip(),
                "page": page_num,
                "section": "",
                "y_pos": 0,
            })

    return text_blocks

def is_scanned_pdf(text_blocks: list) -> bool:
    # If Docling found very little text, likely scanned
    total_text = " ".join(b["text"] for b in text_blocks)
    return len(total_text.strip()) < 100
```

---

## 9. Hierarchical Chunking

**What it is:** A chunking strategy that creates parent chunks (large context) and child chunks (small, precise) linked by parent_chunk_id — enabling both precise retrieval and broad context.

---

### Chunker Implementation
```python
# app/services/ingestion/chunker.py
import uuid
from dataclasses import dataclass, field

@dataclass
class Chunk:
    chunk_id: str
    parent_chunk_id: str | None
    chunk_type: str          # "parent" | "child"
    source_file: str
    page_number: int
    section_title: str
    modality: str            # "text" | "table" | "image"
    content: str
    asset_base64: str | None = None
    y_pos: float = 0.0

def split_into_tokens(text: str, max_tokens: int) -> list[str]:
    words = text.split()
    chunks, current = [], []
    for word in words:
        current.append(word)
        if len(current) >= max_tokens:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks

def build_chunk_tree(
    text_blocks: list[dict],
    tables: list[dict],
    images: list[dict],
    source_file: str,
    parent_tokens: int = 1024,
    child_tokens: int = 256,
) -> list[Chunk]:
    chunks = []

    # Group text blocks by section/page proximity
    sections = group_by_section(text_blocks)

    for section_title, blocks in sections.items():
        full_text = " ".join(b["text"] for b in blocks)
        page = blocks[0]["page"]
        y_pos = blocks[0]["y_pos"]

        # Create parent chunk
        parent_id = str(uuid.uuid4())
        parent_text = " ".join(full_text.split()[:parent_tokens])
        chunks.append(Chunk(
            chunk_id=parent_id,
            parent_chunk_id=None,
            chunk_type="parent",
            source_file=source_file,
            page_number=page,
            section_title=section_title,
            modality="text",
            content=parent_text,
            y_pos=y_pos,
        ))

        # Create child text chunks
        child_texts = split_into_tokens(full_text, child_tokens)
        for child_text in child_texts:
            chunks.append(Chunk(
                chunk_id=str(uuid.uuid4()),
                parent_chunk_id=parent_id,
                chunk_type="child",
                source_file=source_file,
                page_number=page,
                section_title=section_title,
                modality="text",
                content=child_text,
                y_pos=y_pos,
            ))

        # Assign tables on same section as children
        for table in tables:
            if table["page"] == page:
                chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4()),
                    parent_chunk_id=parent_id,
                    chunk_type="child",
                    source_file=source_file,
                    page_number=table["page"],
                    section_title=section_title,
                    modality="table",
                    content=table["markdown"],
                    y_pos=table["y_pos"],
                ))

        # Assign images on same section as children
        for image in images:
            if image["page"] == page:
                chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4()),
                    parent_chunk_id=parent_id,
                    chunk_type="child",
                    source_file=source_file,
                    page_number=image["page"],
                    section_title=section_title,
                    modality="image",
                    content="",        # filled after VLM call
                    asset_base64=None, # filled after optimization
                    y_pos=image["y_pos"],
                ))

    return chunks

def group_by_section(text_blocks: list[dict]) -> dict[str, list[dict]]:
    sections = {}
    current_section = "Introduction"
    for block in text_blocks:
        # Headings are typically shorter and uppercase
        if len(block["text"]) < 80 and block["text"].isupper():
            current_section = block["text"].title()
        sections.setdefault(current_section, []).append(block)
    return sections
```

---

## 10. Pillow — Image Optimization

**What it is:** Python imaging library — used to resize, convert, and compress images before base64 encoding.

---

### Install
```bash
pip install pillow
```

---

### Image Optimizer
```python
# app/services/ingestion/image_optimizer.py
from PIL import Image
import io
import base64

def optimize_image(
    raw_bytes: bytes,
    max_px: int = 1280,
    target_kb: int = 400,
    min_quality: int = 45,
) -> str:
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")

    # Step 1: Resize — maintain aspect ratio
    w, h = img.size
    if max(w, h) > max_px:
        ratio = max_px / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    # Step 2: Convert to WebP with iterative quality reduction
    result_buffer = None
    for quality in [75, 65, 55, min_quality]:
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality)
        size_kb = buffer.tell() / 1024

        if size_kb <= target_kb:
            result_buffer = buffer
            break
        result_buffer = buffer  # keep last attempt even if over target

    result_buffer.seek(0)
    encoded = base64.b64encode(result_buffer.read()).decode("utf-8")
    return f"data:image/webp;base64,{encoded}"
```

---

## 11. asyncio — Concurrent Programming

**What it is:** Python's built-in async library — used to run ingestion Track 1 (text) and Track 2 (images) concurrently.

**Key concepts:** `async def`, `await`, `asyncio.gather`, `asyncio.create_task`

---

### Concurrent Ingestion Tracks
```python
# app/services/ingestion/pipeline.py
import asyncio
from app.services.ingestion.chunker import Chunk

async def process_text_chunk(chunk: Chunk) -> Chunk:
    if len(chunk.content.split()) > 500:
        chunk.content = await summarize_with_llm(chunk.content)
    return chunk

async def process_image_chunk(chunk: Chunk, raw_bytes: bytes) -> Chunk:
    chunk.asset_base64 = optimize_image(raw_bytes)
    result = await caption_with_vlm(chunk.asset_base64)
    chunk.content = result["caption"]
    return chunk

async def run_ingestion_pipeline(document_id: str, chunks: list[Chunk], image_map: dict):
    text_chunks  = [c for c in chunks if c.modality in ("text", "table")]
    image_chunks = [c for c in chunks if c.modality == "image"]

    # Both tracks run at the same time
    text_results, image_results = await asyncio.gather(
        process_text_track(text_chunks),
        process_image_track(image_chunks, image_map),
    )

    all_chunks = text_results + image_results
    await embed_and_store_all(all_chunks)
    await update_document_status(document_id, "completed")

async def process_text_track(chunks: list[Chunk]) -> list[Chunk]:
    tasks = [process_text_chunk(c) for c in chunks]
    return await asyncio.gather(*tasks)

async def process_image_track(chunks: list[Chunk], image_map: dict) -> list[Chunk]:
    tasks = [process_image_chunk(c, image_map[c.chunk_id]) for c in chunks]
    return await asyncio.gather(*tasks)
```

> **Gotcha:** `asyncio.gather()` runs coroutines concurrently in the same thread — it's I/O concurrency, not true parallelism. For CPU-heavy work (like Pillow resizing), use `asyncio.to_thread()` to avoid blocking the event loop.

```python
# For CPU-bound Pillow work
import asyncio

async def process_image_chunk(chunk: Chunk, raw_bytes: bytes) -> Chunk:
    # Run Pillow in a thread so it doesn't block async event loop
    chunk.asset_base64 = await asyncio.to_thread(optimize_image, raw_bytes)
    chunk.content = await caption_with_vlm(chunk.asset_base64)
    return chunk
```

---

## 12. OpenAI API — VLM + LLM

**What it is:** OpenAI's Python SDK — used for GPT-4o VLM image captioning (ingestion) and answer generation (retrieval).

---

### Install
```bash
pip install openai
```

---

### VLM — Image Caption + Classification (Ingestion)
```python
# app/services/ingestion/vlm.py
from openai import AsyncOpenAI
from app.core.config import settings
import json

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def caption_with_vlm(base64_image: str) -> dict:
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": base64_image},
                },
                {
                    "type": "text",
                    "text": """Analyze this image and return a JSON object with:
                    1. "type": one of ["photo", "chart", "graph", "diagram", "screenshot", "table"]
                    2. "caption": a detailed description of the content including any numbers, labels, trends

                    Return only valid JSON, no extra text."""
                }
            ]
        }],
        max_tokens=500,
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)
```

---

### LLM — Answer Generation with Citations (Retrieval)
```python
# app/services/generation/llm.py
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_answer(
    query: str,
    context_chunks: list[dict],
    visual_chunks: list[dict],
) -> str:
    # Build context string
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"[{i}] {chunk['content']}\n\n"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful enterprise knowledge assistant. "
                "Answer using ONLY the provided context. "
                "Reference sources inline as [1], [2], [3]. "
                "If the context is insufficient, say so clearly. "
                "Do not make up information."
            )
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Context:\n{context_text}\n\nQuestion: {query}"}
            ] + [
                # Attach images for visual queries
                {"type": "image_url", "image_url": {"url": c["asset_base64"]}}
                for c in visual_chunks if c.get("asset_base64")
            ]
        }
    ]

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        max_tokens=1000,
    )

    return response.choices[0].message.content
```

> **Gotcha:** GPT-4o has a context window of 128k tokens. Monitor total tokens per request — long documents + many chunks can get expensive fast.

---

## 13. sentence-transformers — BGE Local Embedding

**What it is:** Hugging Face library for running embedding models locally — no API cost, no latency from network calls.

---

### Install
```bash
pip install sentence-transformers
```

---

### Embedding Service
```python
# app/services/ingestion/embedder.py
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import numpy as np

# Load once at startup — cached in memory
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return vectors.tolist()
```

> **Gotcha:** Load the model once at app startup — not per request. Model loading takes 3–5 seconds. Use a singleton pattern as shown above.

> **Gotcha:** BGE models expect a query prefix for retrieval tasks:
```python
def embed_query(query: str) -> list[float]:
    # BGE requires this prefix for queries (not for documents)
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    return embed_text(prefixed)

def embed_document(text: str) -> list[float]:
    # No prefix for document chunks
    return embed_text(text)
```

---

## 14. BM25 — Sparse Embedding

**What it is:** Classic keyword-based retrieval algorithm — ranks documents by term frequency and rarity. Catches exact keyword matches that semantic search misses.

---

### Install
```bash
pip install rank-bm25
```

---

### BM25 Index + Search
```python
# app/services/ingestion/embedder.py (continued)
from rank_bm25 import BM25Okapi
import pickle

def tokenize(text: str) -> list[str]:
    return text.lower().split()

class BM25Index:
    def __init__(self):
        self.corpus_tokens: list[list[str]] = []
        self.chunk_ids: list[str] = []
        self.index: BM25Okapi | None = None

    def add_document(self, chunk_id: str, text: str):
        self.corpus_tokens.append(tokenize(text))
        self.chunk_ids.append(chunk_id)

    def build(self):
        self.index = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        query_tokens = tokenize(query)
        scores = self.index.get_scores(query_tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(self.chunk_ids[i], float(scores[i])) for i in top_indices]

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str) -> "BM25Index":
        with open(path, "rb") as f:
            return pickle.load(f)
```

> **Gotcha:** BM25 is an in-memory index. For MVP (100 documents) this is fine. For production, Qdrant supports native sparse vectors — migrate there in Phase 2.

---

## 15. Qdrant — Vector Database

**What it is:** Open-source vector database — stores dense + sparse vectors alongside metadata (payload). Supports hybrid search natively.

---

### Install
```bash
pip install qdrant-client
```

---

### Create Collection
```python
# app/services/ingestion/storer.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, SparseVectorParams, CreateCollection
)
from app.core.config import settings

client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

async def create_collection_if_not_exists():
    collections = await client.get_collections()
    names = [c.name for c in collections.collections]

    if settings.QDRANT_COLLECTION not in names:
        await client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
            sparse_vectors_config={
                "bm25": SparseVectorParams()
            }
        )
```

---

### Store a Chunk
```python
from qdrant_client.models import PointStruct, SparseVector
from app.services.ingestion.chunker import Chunk

async def store_chunk(chunk: Chunk, dense_vector: list[float], sparse_tokens: dict):
    await client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=chunk.chunk_id,
                vector={
                    "": dense_vector,           # default dense vector
                    "bm25": SparseVector(
                        indices=sparse_tokens["indices"],
                        values=sparse_tokens["values"],
                    )
                },
                payload={
                    "chunk_id":        chunk.chunk_id,
                    "parent_chunk_id": chunk.parent_chunk_id,
                    "chunk_type":      chunk.chunk_type,
                    "source_file":     chunk.source_file,
                    "page_number":     chunk.page_number,
                    "section_title":   chunk.section_title,
                    "modality":        chunk.modality,
                    "content":         chunk.content,
                    "asset_base64":    chunk.asset_base64,
                    "language":        "en",
                }
            )
        ]
    )
```

---

### Hybrid Search
```python
# app/services/retrieval/searcher.py
from qdrant_client.models import SearchRequest, NamedVector, NamedSparseVector, SparseVector, Filter, FieldCondition, MatchValue
import asyncio

async def hybrid_search(
    query_dense: list[float],
    query_sparse: dict,
    top_k: int = 10,
    modality_filter: str | None = None,
) -> tuple[list, list]:

    # Build optional filter
    search_filter = None
    if modality_filter:
        search_filter = Filter(must=[
            FieldCondition(key="modality", match=MatchValue(value=modality_filter))
        ])

    # Run dense and sparse searches in parallel
    dense_task = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=NamedVector(name="", vector=query_dense),
        query_filter=search_filter,
        limit=top_k,
        with_payload=True,
    )

    sparse_task = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=NamedSparseVector(
            name="bm25",
            vector=SparseVector(
                indices=query_sparse["indices"],
                values=query_sparse["values"],
            )
        ),
        query_filter=search_filter,
        limit=top_k,
        with_payload=True,
    )

    dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)
    return dense_results, sparse_results
```

---

## 16. Redis — Caching

**What it is:** In-memory key-value store — used for L1 Answer Cache and L2 Embedding Cache.

---

### Install
```bash
pip install redis[asyncio]
```

---

### Redis Cache Service
```python
# app/services/retrieval/cache.py
import redis.asyncio as aioredis
import hashlib
import json
import pickle
from app.core.config import settings

redis_client = aioredis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=False,
)

def make_key(prefix: str, text: str) -> str:
    return f"cache:{prefix}:{hashlib.md5(text.encode()).hexdigest()}"

# L1 — Answer Cache
async def get_cached_answer(query: str) -> dict | None:
    key = make_key("answer", query)
    data = await redis_client.get(key)
    return json.loads(data) if data else None

async def set_cached_answer(query: str, answer: dict, ttl: int = 3600):
    key = make_key("answer", query)
    await redis_client.setex(key, ttl, json.dumps(answer))

async def invalidate_answer_cache():
    # Flush all answer cache keys on new document ingestion
    keys = await redis_client.keys("cache:answer:*")
    if keys:
        await redis_client.delete(*keys)

# L2 — Embedding Cache
async def get_cached_embedding(query: str) -> list[float] | None:
    key = make_key("embed", query)
    data = await redis_client.get(key)
    return pickle.loads(data) if data else None

async def set_cached_embedding(query: str, vector: list[float], ttl: int = 604800):
    key = make_key("embed", query)
    await redis_client.setex(key, ttl, pickle.dumps(vector))
```

---

## 17. RRF Fusion

**What it is:** Reciprocal Rank Fusion — merges ranked lists from dense and sparse search into a single unified ranking. Simple but highly effective.

**Formula:** `score(chunk) = 1/(rank_dense + 60) + 1/(rank_sparse + 60)`

---

### RRF Implementation
```python
# app/services/retrieval/fusion.py

RELEVANCE_THRESHOLD = 0.02  # tune based on testing

def rrf_fusion(
    dense_results: list,
    sparse_results: list,
    k: int = 60,
) -> list[dict]:
    scores: dict[str, float] = {}
    payloads: dict[str, dict] = {}

    for rank, result in enumerate(dense_results):
        chunk_id = result.payload["chunk_id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (rank + k)
        payloads[chunk_id] = result.payload

    for rank, result in enumerate(sparse_results):
        chunk_id = result.payload["chunk_id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (rank + k)
        payloads[chunk_id] = result.payload

    # Sort by RRF score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [
        {"chunk_id": cid, "rrf_score": score, "payload": payloads[cid]}
        for cid, score in ranked
    ]

def apply_relevance_threshold(
    ranked_chunks: list[dict],
    threshold: float = RELEVANCE_THRESHOLD,
) -> list[dict]:
    return [c for c in ranked_chunks if c["rrf_score"] >= threshold]
```

---

## 18. Next.js App Router

**What it is:** React framework with file-based routing, server components, and full-stack capabilities.

**Key concepts:** App Router, server vs client components, layouts, route handlers

---

### Folder Structure Pattern
```
app/
├── layout.tsx          ← root layout (fonts, providers)
├── page.tsx            ← home (redirect to /chat or /auth/login)
├── auth/
│   ├── login/
│   │   └── page.tsx    ← login page (client component)
│   └── verify-otp/
│       └── page.tsx
├── chat/
│   └── page.tsx        ← main chat page (client component)
└── admin/
    └── documents/
        └── page.tsx    ← admin dashboard (client component)
```

---

### Root Layout with Providers
```tsx
// app/layout.tsx
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "@/components/providers"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Astrynox AI",
  description: "Enterprise Knowledge Assistant",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

---

### Providers (TanStack Query + Auth)
```tsx
// components/providers.tsx
"use client"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        retry: 1,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

---

### Protected Route
```tsx
// components/protected-route.tsx
"use client"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { getAccessToken } from "@/lib/auth"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    if (!getAccessToken()) {
      router.push("/auth/login")
    }
  }, [])

  return <>{children}</>
}
```

---

## 19. Tailwind CSS + shadcn/ui

**What it is:** Tailwind is utility-first CSS. shadcn/ui is a collection of accessible, unstyled components built on Radix UI that you copy into your project and own.

---

### Install shadcn/ui
```bash
npx shadcn@latest init
# Choose: TypeScript, App Router, Tailwind
# Then add components as needed:
npx shadcn@latest add button input card badge textarea
```

---

### Chat Input Component
```tsx
// components/chat/ChatInput.tsx
"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from "lucide-react"

interface ChatInputProps {
  onSubmit: (query: string) => void
  isLoading: boolean
}

export function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const [value, setValue] = useState("")

  const handleSubmit = () => {
    if (!value.trim() || isLoading) return
    onSubmit(value.trim())
    setValue("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex gap-2 p-4 border-t bg-background">
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about company documents..."
        className="min-h-[52px] max-h-[200px] resize-none"
        disabled={isLoading}
      />
      <Button onClick={handleSubmit} disabled={isLoading || !value.trim()} size="icon">
        <Send className="h-4 w-4" />
      </Button>
    </div>
  )
}
```

---

### Image Citation Component
```tsx
// components/citations/ImageCitation.tsx
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ImageCitationProps {
  id: number
  sourceFile: string
  pageNumber: number
  sectionTitle: string
  caption: string
  assetBase64: string
}

export function ImageCitation({ id, sourceFile, pageNumber, sectionTitle, caption, assetBase64 }: ImageCitationProps) {
  return (
    <Card className="mt-2">
      <CardContent className="pt-4 space-y-2">
        <div className="flex items-center gap-2">
          <Badge variant="outline">[{id}]</Badge>
          <Badge variant="secondary">Image</Badge>
          <span className="text-sm text-muted-foreground">
            {sourceFile} — p.{pageNumber}, {sectionTitle}
          </span>
        </div>
        <img
          src={assetBase64}
          alt={caption}
          className="rounded-md max-h-64 object-contain w-full border"
        />
        <p className="text-xs text-muted-foreground italic">{caption}</p>
      </CardContent>
    </Card>
  )
}
```

---

## 20. TanStack Query

**What it is:** Async state management for server data — handles fetching, caching, refetching, and mutations. Eliminates manual `useEffect` + `useState` for API calls.

**Key concepts:** `useQuery` (GET), `useMutation` (POST/DELETE), query keys, invalidation

---

### Install
```bash
npm install @tanstack/react-query
```

---

### API Client
```ts
// lib/api.ts
import axios from "axios"
import { getAccessToken, refreshAccessToken } from "./auth"

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      await refreshAccessToken()
      return api.request(err.config)
    }
    return Promise.reject(err)
  }
)
```

---

### useDocuments Hook
```ts
// hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: async () => {
      const { data } = await api.get("/api/documents/")
      return data
    },
  })
}

export function useDeleteDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (documentId: string) => {
      await api.delete(`/api/documents/${documentId}`)
    },
    onSuccess: () => {
      // Automatically refetch document list after delete
      queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
  })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append("file", file)
      const { data } = await api.post("/api/documents/upload", formData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
  })
}
```

---

### useChat Hook
```ts
// hooks/useChat.ts
import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"

interface QueryResponse {
  answer: string
  citations: Citation[]
  from_cache: boolean
  response_time_ms: number
}

export function useChat() {
  return useMutation({
    mutationFn: async (query: string): Promise<QueryResponse> => {
      const { data } = await api.post("/api/query", { query })
      return data
    },
  })
}
```

---

### Using Hooks in Chat Page
```tsx
// app/chat/page.tsx
"use client"
import { useState } from "react"
import { useChat } from "@/hooks/useChat"
import { ChatInput } from "@/components/chat/ChatInput"
import { ChatMessage } from "@/components/chat/ChatMessage"

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([])
  const { mutate: sendQuery, isPending } = useChat()

  const handleSubmit = (query: string) => {
    setMessages(prev => [...prev, { role: "user", content: query }])

    sendQuery(query, {
      onSuccess: (data) => {
        setMessages(prev => [...prev, {
          role: "assistant",
          content: data.answer,
          citations: data.citations,
          fromCache: data.from_cache,
        }])
      },
      onError: () => {
        setMessages(prev => [...prev, {
          role: "assistant",
          content: "Something went wrong. Please try again.",
          citations: [],
        }])
      }
    })
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
        {isPending && (
          <div className="text-muted-foreground text-sm animate-pulse">
            Searching documents...
          </div>
        )}
      </div>
      <ChatInput onSubmit={handleSubmit} isLoading={isPending} />
    </div>
  )
}
```

> **Gotcha:** TanStack Query caches by `queryKey`. Always include dynamic IDs in the key: `["documents", documentId]` not just `["documents"]` when fetching a single item.

---

## Progress Tracker

Tick off each task as you complete it. Follow the sprint order — don't jump ahead.

---

### Sprint 1 — Week 1: Foundation & Auth

#### FastAPI
- [ ] Read: fastapi.tiangolo.com/tutorial — Quick Start, Routing, Dependency Injection
- [ ] Run: Basic app setup example from Section 1 of this guide
- [ ] Scratch: `scratch/test_fastapi.py` — one working route with a dependency
- [ ] Done when: FastAPI server starts and `/api/auth/login` route responds

#### SQLAlchemy + Alembic
- [ ] Read: SQLAlchemy 2.0 docs — "ORM Quickstart" section only
- [ ] Read: alembic.sqlalchemy.org — "Tutorial" page only
- [ ] Run: Async session setup + User model from Section 2 of this guide
- [ ] Scratch: `scratch/test_db.py` — create a user and query it
- [ ] Run: `alembic init alembic` and `alembic revision --autogenerate`
- [ ] Done when: `alembic upgrade head` creates users + documents tables in PostgreSQL

#### Pydantic
- [ ] Read: pydantic.dev/concepts — "Models" section only
- [ ] Run: Schemas from Section 3 of this guide
- [ ] Done when: `LoginRequest` and `QueryResponse` schemas validate correctly

#### JWT Authentication
- [ ] Read: python-jose README (5 min)
- [ ] Run: JWT utilities from Section 4 of this guide in scratch
- [ ] Scratch: `scratch/test_jwt.py` — generate a token and decode it
- [ ] Done when: Login returns a JWT and a protected route rejects invalid tokens

#### Google OAuth2
- [ ] Read: Google "Web Server" OAuth2 guide
- [ ] Create: Google Cloud Console project + OAuth2 credentials
- [ ] Run: `exchange_google_code()` from Section 5 of this guide
- [ ] Done when: Google login redirects correctly and returns a JWT

#### Resend (OTP Email)
- [ ] Read: resend.com/docs — Python section (5 min)
- [ ] Create: Resend account + API key
- [ ] Run: `send_otp_email()` from Section 6 of this guide
- [ ] Done when: OTP email arrives in inbox after login attempt

#### Next.js App Router
- [ ] Read: nextjs.org/learn — complete the official interactive course
- [ ] Run: `npx create-next-app@latest frontend` with App Router + TypeScript + Tailwind
- [ ] Build: Login page, register page, OTP verify page
- [ ] Done when: Login form submits to FastAPI and stores JWT

#### shadcn/ui Setup
- [ ] Run: `npx shadcn@latest init` in the frontend folder
- [ ] Add: `npx shadcn@latest add button input card badge textarea`
- [ ] Done when: A shadcn Button renders correctly on the login page

---

### Sprint 2 — Week 2: Ingestion Pipeline

#### Docling
- [ ] Read: docling.dev docs + GitHub README examples
- [ ] Install: `pip install docling`
- [ ] Scratch: `scratch/test_docling.py` — parse a sample PDF and print text blocks
- [ ] Done when: Text, tables, and images extracted from a real PDF with page numbers

#### Tesseract OCR
- [ ] Install: Tesseract binary from github.com/UB-Mannheim/tesseract/wiki
- [ ] Install: `pip install pytesseract pdf2image`
- [ ] Scratch: `scratch/test_ocr.py` — run OCR on a scanned PDF page
- [ ] Done when: Text extracted from a scanned document image

#### Hierarchical Chunking
- [ ] Read: Section 9 of this guide fully
- [ ] Scratch: `scratch/test_chunker.py` — chunk a sample text and print parent + children
- [ ] Done when: Parent chunk and child chunks created with correct parent_chunk_id links

#### Pillow (Image Optimization)
- [ ] Read: pillow.readthedocs.io — Image class section
- [ ] Install: `pip install pillow`
- [ ] Scratch: `scratch/test_optimizer.py` — optimize a test image and check output size
- [ ] Done when: A 2MB JPEG comes out under 400KB as WebP base64

#### asyncio
- [ ] Read: realpython.com/async-io-python — full article (most important read in Sprint 2)
- [ ] Run: Concurrent tracks example from Section 11 of this guide
- [ ] Scratch: `scratch/test_async.py` — run two async tasks with `asyncio.gather()`
- [ ] Done when: Text track and image track run concurrently without blocking each other

#### OpenAI API — VLM (Image Captioning)
- [ ] Read: platform.openai.com/docs — Vision section
- [ ] Install: `pip install openai`
- [ ] Scratch: `scratch/test_vlm.py` — send a base64 image to GPT-4o and get a caption
- [ ] Done when: VLM returns JSON with `type` and `caption` for a chart image

#### sentence-transformers (BGE)
- [ ] Read: sbert.net/docs/quickstart — Usage section
- [ ] Install: `pip install sentence-transformers torch`
- [ ] Scratch: `scratch/test_embed.py` — embed a sentence and print the vector shape
- [ ] Done when: BGE model loads and returns a 1024-dim vector for a text chunk

#### BM25
- [ ] Read: rank-bm25 GitHub README (5 min)
- [ ] Install: `pip install rank-bm25`
- [ ] Scratch: `scratch/test_bm25.py` — build a small index and search it
- [ ] Done when: BM25 returns ranked results for a keyword query

#### Qdrant
- [ ] Read: qdrant.tech/documentation/quickstart
- [ ] Run: Docker Compose to start Qdrant locally
- [ ] Scratch: `scratch/test_qdrant.py` — create collection, upsert a chunk, search it
- [ ] Done when: A chunk stored in Qdrant is retrieved by a dense vector search

---

### Sprint 3 — Week 3: Retrieval Pipeline & Redis Cache

#### Qdrant Hybrid Search
- [ ] Read: qdrant.tech/documentation/concepts/search — Sparse Vectors section
- [ ] Scratch: `scratch/test_hybrid_search.py` — run dense + sparse search in parallel
- [ ] Done when: Both dense and sparse results returned from a single query

#### Redis Caching
- [ ] Read: redis-py GitHub README
- [ ] Install: `pip install redis[asyncio]`
- [ ] Run: Docker Compose to start Redis locally
- [ ] Scratch: `scratch/test_redis.py` — set and get a cached value with TTL
- [ ] Done when: L1 Answer Cache and L2 Embedding Cache set/get/invalidate correctly

#### RRF Fusion
- [ ] Read: Section 17 of this guide
- [ ] Scratch: `scratch/test_rrf.py` — merge two ranked lists and print unified scores
- [ ] Done when: RRF correctly merges dense + sparse results and relevance threshold filters low scores

---

### Sprint 4 — Week 4: Generation, Citations & Frontend

#### OpenAI API — LLM Generation
- [ ] Read: platform.openai.com/docs — Chat Completions section
- [ ] Run: LLM generation example from Section 12 of this guide
- [ ] Done when: GPT-4o returns a cited answer with inline [1][2][3] references

#### TanStack Query
- [ ] Read: tanstack.com/query/latest/docs/framework/react/quick-start
- [ ] Install: `npm install @tanstack/react-query`
- [ ] Run: `useDocuments` and `useChat` hooks from Section 20 of this guide
- [ ] Done when: Document list fetches from API, chat mutation sends query and returns answer

#### Tailwind CSS
- [ ] Read: tailwindcss.com/docs — Core Concepts section (Utility-First, Responsive, Dark Mode)
- [ ] Done when: Chat UI is styled with Tailwind utility classes

#### shadcn/ui Components
- [ ] Add components as needed: `npx shadcn@latest add <component>`
- [ ] Build: `ChatInput`, `CitationBlock`, `ImageCitation`, `TableCitation`
- [ ] Build: `DocumentList`, `UploadForm`, `StatusBadge`
- [ ] Done when: Full chat UI renders with citations including base64 images

---

### Overall Completion

- [ ] Sprint 1 complete — Auth system + Admin upload UI working
- [ ] Sprint 2 complete — Full ingestion pipeline working end-to-end
- [ ] Sprint 3 complete — Full retrieval pipeline with cache working
- [ ] Sprint 4 complete — Full system working: chat → cited answer with visuals

---

*Astrynox AI — Learning Guide v1.0*
