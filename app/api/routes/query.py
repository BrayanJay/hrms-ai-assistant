from fastapi import APIRouter, Depends

from app.schemas.query import QueryRequest, QueryResponse
from app.api.dependencies import require_user
from app.services.retrieval.cache import get_answer
from app.services.retrieval.pipeline import retrieve

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query(req: QueryRequest, current_user: dict = Depends(require_user)):
    cache_result = await get_answer(req.query)

    if cache_result:
        return QueryResponse(answer=cache_result, citations=[])
    
    context = await retrieve(req.query)

    if not context:
        return QueryResponse(answer="I don't have enough information to answer that question.", citations=[])
    
    return QueryResponse(answer="", citations=context)