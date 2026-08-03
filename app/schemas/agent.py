from pydantic import BaseModel

class RouterDecision(BaseModel):
    intent: str
    language: str
    rag_query: str | None
    tool_name: str | None
    tool_params: dict | None
    is_sequential: bool
    is_write: bool
    chat_response_hint: str | None

class ConfirmRequest(BaseModel):
    session_id: str
    action_id: str
    confirmed: bool