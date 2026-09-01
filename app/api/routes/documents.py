from app.schemas.document import UploadResponse, DocumentListItem
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.document import Document
from app.services.ingestion.pipeline import run_pipeline
from app.services.ingestion.storer import delete_doc_chunks
from app.services.retrieval.cache import invalidate_answers
from app.core.logging import get_logger

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from sqlalchemy import select
import aiofiles

router = APIRouter()
logger = get_logger(__name__)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(backgroud_tasks: BackgroundTasks, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_admin)):
    file_type = Path(file.filename).suffix.lower().lstrip(".")

    if file_type not in ["pdf", "docx", 'pptx', 'xlsx']:
        logger.warning("upload rejected — invalid file type", extra={"user_id": current_user["sub"], "filename": file.filename, "file_type": file_type})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )

    existing = await db.execute(
        select(Document).where(
            Document.filename == file.filename,
            Document.uploaded_by == current_user["sub"]
        )
    )
    old_doc = existing.scalar_one_or_none()
    if old_doc:
        logger.info("replacing existing document", extra={"user_id": current_user["sub"], "filename": file.filename, "old_doc_id": str(old_doc.id)})
        await delete_doc_chunks(str(old_doc.id))
        await invalidate_answers()
        await db.delete(old_doc)
        await db.flush()

    new_doc = Document(filename=file.filename, original_filename=file.filename, status="processing", file_type=file_type, source_type="document", uploaded_by=current_user["sub"])
    db.add(new_doc)
    await db.flush()

    doc_id = new_doc.id
    doc_filename = new_doc.filename
    doc_status = new_doc.status
    doc_created_at = new_doc.created_at

    await db.commit()

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = str(upload_dir / file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())

    logger.info("document uploaded — pipeline queued", extra={"user_id": current_user["sub"], "doc_id": str(doc_id), "filename": doc_filename, "file_type": file_type})
    backgroud_tasks.add_task(run_pipeline, str(doc_id), file_path, db)
    return UploadResponse(id=doc_id, filename=doc_filename, status=doc_status, created_at=doc_created_at)

@router.get("/", response_model=list[DocumentListItem])
async def list_documents(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_admin)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    return documents

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
    logger.info("document deleted", extra={"user_id": current_user["sub"], "doc_id": doc_id, "filename": doc.filename})