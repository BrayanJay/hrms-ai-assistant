from fastapi import APIRouter, Depends

from app.schemas.query import QueryRequest, QueryResponse
from app.api.dependencies import require_user
from app.services.retrieval.cache import get_answer, set_answer, get_history, set_history
from app.services.retrieval.pipeline import retrieve
from app.services.generation.llm import generate
from app.services.generation.citation_builder import build_citations

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query(req: QueryRequest, current_user: dict = Depends(require_user)):

    cache_result = await get_answer(req.query)

    if cache_result:
        return QueryResponse(answer=cache_result, citations=[])
    
    history = await get_history(user_id=current_user["sub"], session_id=req.session_id)
    history = history or []

    context = await retrieve(req.query, history)

    if not context:
        return QueryResponse(answer="I don't have enough information to answer that question.", citations=[])

    answer = await generate(query=req.query, context=context, history=history)
    await set_answer(req.query, answer)

    history.append({"role":"user", "content": req.query})
    history.append({"role":"assistant", "content": answer})
    await set_history(user_id=current_user["sub"], session_id=req.session_id, history=history)

    citations = build_citations(answer, context)

    return QueryResponse(answer=answer, citations=citations)