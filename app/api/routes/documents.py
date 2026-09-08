import base64
import json
import secrets

from app.api.dependencies import require_admin, require_user
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.logging import get_logger
from app.models.document import Document
from app.schemas.document import UploadResponse, DocumentListItem
from app.services.ingestion.pipeline import run_pipeline
from app.services.ingestion.storer import delete_doc_chunks
from app.services.retrieval.cache import invalidate_answers, redis

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

router = APIRouter()
logger = get_logger(__name__)

DL_TOKEN_PREFIX = "dl:"
DL_TOKEN_TTL = 60  # seconds


def _validate_jwt(raw_token: str) -> None:
    try:
        padded = raw_token.split(".")[1]
        padded += "=" * (-len(padded) % 4)
        json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    backgroud_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form("policy"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    file_type = Path(file.filename).suffix.lower().lstrip(".")

    if file_type not in ["pdf", "docx", "pptx"]:
        logger.warning("upload rejected — invalid file type", extra={"user_id": current_user["sub"], "doc_filename": file.filename, "file_type": file_type})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")

    existing = await db.execute(
        select(Document).where(
            Document.filename == file.filename,
            Document.uploaded_by == current_user["sub"],
        )
    )
    old_doc = existing.scalar_one_or_none()
    if old_doc:
        logger.info("replacing existing document", extra={"user_id": current_user["sub"], "doc_filename": file.filename, "old_doc_id": str(old_doc.id)})
        await delete_doc_chunks(str(old_doc.id))
        await invalidate_answers()
        await db.delete(old_doc)
        await db.flush()

    if category not in ("policy", "navigation", "company-information"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category must be 'policy', 'navigation', or 'company-information'")

    new_doc = Document(
        filename=file.filename,
        original_filename=file.filename,
        status="processing",
        file_type=file_type,
        source_type="document",
        doc_category=category,
        uploaded_by=current_user["sub"],
    )
    db.add(new_doc)
    await db.flush()

    doc_id = new_doc.id
    doc_filename = new_doc.filename
    doc_status = new_doc.status
    doc_category = new_doc.doc_category
    doc_created_at = new_doc.created_at

    await db.commit()

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = str(upload_dir / file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())

    logger.info("document uploaded — pipeline queued", extra={"user_id": current_user["sub"], "doc_id": str(doc_id), "doc_filename": doc_filename, "file_type": file_type, "doc_category": doc_category})
    backgroud_tasks.add_task(run_pipeline, str(doc_id), file_path, db)
    return UploadResponse(id=doc_id, filename=doc_filename, status=doc_status, doc_category=doc_category, created_at=doc_created_at)


@router.get("/", response_model=list[DocumentListItem])
async def list_documents(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_admin)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_admin)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        logger.warning("delete failed — document not found", extra={"user_id": current_user["sub"], "doc_id": doc_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await delete_doc_chunks(doc_id)
    await invalidate_answers()
    await db.delete(doc)
    await db.commit()
    logger.info("document deleted", extra={"user_id": current_user["sub"], "doc_id": doc_id, "doc_filename": doc.filename})


@router.post("/{doc_id}/download-token")
@limiter.limit("10/minute")
async def create_download_token(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_user),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")

    token = secrets.token_urlsafe(32)
    # Store doc_id and user_id together — token is bound to the requesting user
    await redis.setex(f"{DL_TOKEN_PREFIX}{token}", DL_TOKEN_TTL, f"{doc_id}:{current_user['sub']}")

    logger.info("download token issued", extra={"user_id": current_user["sub"], "doc_id": doc_id})
    return JSONResponse({"url": f"/api/documents/download/{token}"})


@router.get("/download/{token}")
async def download_by_token(token: str, db: AsyncSession = Depends(get_db)):
    stored = await redis.getdel(f"{DL_TOKEN_PREFIX}{token}")
    if not stored:
        raise HTTPException(status_code=401, detail="Invalid or expired download link")

    doc_id, user_id = stored.split(":", 1)

    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path("uploads") / doc.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    logger.info("document downloaded via token", extra={"user_id": user_id, "doc_id": doc_id, "doc_filename": doc.filename})
    return FileResponse(
        path=str(file_path),
        filename=doc.original_filename,
        media_type="application/octet-stream",
        headers={"Referrer-Policy": "no-referrer"},
    )


@router.get("/{doc_id}/view")
async def view_document(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: str | None = Query(default=None),
):
    raw_token = token or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not raw_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    _validate_jwt(raw_token)

    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path("uploads") / doc.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_type = "application/pdf" if doc.file_type == "pdf" else "application/octet-stream"
    return FileResponse(
        path=str(file_path),
        filename=doc.original_filename,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename=\"{doc.original_filename}\""},
    )
