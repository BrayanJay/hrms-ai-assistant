from fastapi import APIRouter, Depends

from app.schemas.query import QueryRequest, QueryResponse
from app.api.dependencies import require_user
from app.services.retrieval.cache import get_answer, set_answer
from app.services.retrieval.pipeline import retrieve
from app.services.generation.llm import generate
from app.services.generation.citation_builder import build_citations

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query(req: QueryRequest, current_user: dict = Depends(require_user)):
    cache_result = await get_answer(req.query)

    if cache_result:
        return QueryResponse(answer=cache_result, citations=[])
    
    context = await retrieve(req.query)

    if not context:
        return QueryResponse(answer="I don't have enough information to answer that question.", citations=[])
    
    answer = await generate(query=req.query, context=context)
    await set_answer(req.query, answer)

    citations = build_citations(answer, context)

    return QueryResponse(answer=answer, citations=citations)