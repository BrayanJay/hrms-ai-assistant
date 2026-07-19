from pydantic import BaseModel

class ChatSessionResponse(BaseModel):
    session_id: str