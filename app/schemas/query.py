from pydantic import BaseModel

class QueryRequest(BaseModel):
    session_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    citations: list[dict]