from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.schemas.document import UploadResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import require_admin
from pathlib import Path
from app.models.document import Document

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), admin_id: str = Depends(require_admin)):
    file_type = Path(file.filename).suffix.lower().lstrip(".")
    
    if file_type not in ["pdf", "docx", 'pptx', 'xlsx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    new_doc = Document(filename=file.filename, original_filename=file.filename, status="processing", file_type=file_type, source_type="document", uploaded_by=admin_id)
    db.add(new_doc)
    await db.flush()

    doc_id = new_doc.id
    doc_filename = new_doc.filename
    doc_status = new_doc.status
    doc_created_at = new_doc.created_at

    await db.commit()

    return UploadResponse(document_id=doc_id, filename=doc_filename, status=doc_status, created_at=doc_created_at)
    
    
