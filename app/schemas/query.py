import re
from pydantic import BaseModel, Field, field_validator

class QueryRequest(BaseModel):
    session_id: str
    query: str = Field(..., max_length=2000)

    @field_validator("query")
    @classmethod
    def strip_html(cls, v: str):
        return re.sub(r"<[^>]+>", "", v).strip()

class QueryResponse(BaseModel):
    answer: str
    citations: list[dict]
    requires_confirmation: bool = False
    confirmation_payload: dict | None = None
    pending_action_id: str | None = None