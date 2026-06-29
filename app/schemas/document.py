from pydantic import BaseModel
import uuid
from datetime import datetime
class UploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    created_at: datetime

class DocumentListItem(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    filename: str
    file_type: str
    status: str
    created_at: datetime