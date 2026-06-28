from pydantic import BaseModel
import uuid
from datetime import datetime
class UploadResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str
    created_at: datetime