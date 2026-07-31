from fastapi import APIRouter, Depends, Request
import time
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.schemas.query import QueryRequest, QueryResponse
from app.models.query_event import QueryEvent
from app.api.dependencies import require_user
from app.services.retrieval.cache import get_answer, set_answer, get_history, set_history
from app.services.retrieval.pipeline import retrieve
from app.services.generation.llm import generate
from app.services.generation.citation_builder import build_citations
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query(request: Request, req: QueryRequest, current_user: dict = Depends(require_user), db: AsyncSession = Depends(get_db)):
    start_time = time.monotonic()
    cache_hit = False
    answer = None
    citations = []
    retrieved_chunks = 0

    cache_result = await get_answer(req.query)

    if cache_result:
        cache_hit = True
        answer = cache_result

    else:
        history = await get_history(user_id=current_user["sub"], session_id=req.session_id)
        history = history or []
        
        context = await retrieve(req.query, history)
        if context:
            retrieved_chunks = len(context)
            answer = await generate(query=req.query, context=context, history=history)
            await set_answer(req.query, answer)

            history.append({"role":"user", "content": req.query})
            history.append({"role":"assistant", "content": answer})
            await set_history(user_id=current_user["sub"], session_id=req.session_id, history=history)

            citations = build_citations(answer, context)

    if not answer:
      answer = "I don't have enough information to answer that question."
      
    response_time_ms = int((time.monotonic() - start_time) * 1000)
    query_event = QueryEvent(user_id=current_user["sub"], session_id=req.session_id, query=req.query, cache_hit=cache_hit, retrieved_chunks=retrieved_chunks, response_time_ms=response_time_ms)
    db.add(query_event)
    await db.commit()

    return QueryResponse(answer=answer, citations=citations)