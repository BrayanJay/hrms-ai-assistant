import asyncio
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import require_user
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.logging import get_logger
from app.models.agent_log import AgentLog
from app.models.query_event import QueryEvent
from app.schemas.agent import ConfirmRequest
from app.schemas.query import QueryRequest, QueryResponse
from app.services.generation.citation_builder import build_citations
from app.services.generation.llm import generate
from app.services.retrieval.cache import get_answer, get_history, set_answer, set_history
from app.services.retrieval.pipeline import retrieve
from app.services.router.intent import classify_intent
from app.services.tools.executor import ToolCallError, execute_tool
from app.services.tools.pending import delete_pending, get_pending, set_pending
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.generation.translator import to_english, from_english
from app.services.generation.summarizer import compact_history
from app.services.tools.transformer import transform_tool_result

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query(request: Request, req: QueryRequest, current_user: dict = Depends(require_user), db: AsyncSession = Depends(get_db)):
    start_time = time.monotonic()
    user_id = current_user["sub"]
    user_token = request.headers.get("Authorization", "").split(" ")[1]

    history = await get_history(user_id=user_id, session_id=req.session_id) or []
    history = await compact_history(history)
    router_context = history[-4:] if len(history) > 4 else history

    t0 = time.perf_counter()
    decision = await classify_intent(query=req.query, context=router_context)
    logger.info("intent classified", extra={
        "user_id": user_id,
        "query": req.query[:100],
        "intent": decision.intent,
        "language": decision.language,
        "tool": decision.tool_name,
        "rag_query": decision.rag_query,
        "duration_s": round(time.perf_counter() - t0, 2),
    })

    english_query = await to_english(req.query, decision.language)

    answer = None
    citations = []
    tool_result = None
    retrieved_chunks = 0
    cache_hit = False
    requires_confirmation = False
    pending_action_id = None
    confirmation_payload = None

    if decision.intent == "CHAT":
        t0 = time.perf_counter()
        answer = await generate(
            query=english_query,
            context=[],
            history=history,
            chat_hint=decision.chat_response_hint,
            language=decision.language
        )
        logger.info("chat response generated", extra={"user_id": user_id, "duration_s": round(time.perf_counter() - t0, 2)})

    elif decision.intent == "RAG":
        cache_result = await get_answer(english_query)
        if cache_result:
            cache_hit = True
            answer = cache_result["answer"]
            citations = cache_result["citations"]
            logger.info("L1 cache hit — skipping retrieval and generation", extra={"user_id": user_id, "query": req.query[:100]})
        else:
            context = await retrieve(decision.rag_query or english_query, history)
            retrieved_chunks = len(context) if context else 0
            if context:
                t0 = time.perf_counter()
                answer = await generate(query=english_query, context=context, history=history, language=decision.language)
                logger.info("RAG response generated", extra={"user_id": user_id, "chunks_used": retrieved_chunks, "duration_s": round(time.perf_counter() - t0, 2)})
                citations = build_citations(answer, context)
                await set_answer(english_query, answer, citations)

    elif decision.intent == "TOOL":
        if decision.is_write:
            action_id = str(uuid.uuid4())
            payload = {
                "tool_name": decision.tool_name,
                "tool_params": decision.tool_params or {},
                "query": req.query,
            }
            await set_pending(session_id=req.session_id, action_id=action_id, payload=payload)
            requires_confirmation = True
            pending_action_id = action_id
            confirmation_payload = payload
            answer = "I need your confirmation to proceed with this action."
            logger.info("maker-checker triggered", extra={"user_id": user_id, "tool": decision.tool_name, "action_id": action_id})
        else:
            try:
                tool_result = await execute_tool(
                    decision.tool_name, decision.tool_params or {}, user_token
                )
                tool_result = transform_tool_result(decision.tool_name, tool_result)
                t0 = time.perf_counter()
                answer = await generate(
                    query=english_query,
                    context=[],
                    history=history,
                    tool_context=tool_result,
                    language=decision.language
                )
                logger.info("tool response generated", extra={"user_id": user_id, "tool": decision.tool_name, "duration_s": round(time.perf_counter() - t0, 2)})
            except ToolCallError:
                logger.warning("tool call failed", extra={"user_id": user_id, "tool": decision.tool_name})
                answer = "I couldn't retrieve that information right now. Please try again later."

    elif decision.intent == "BOTH":
        results = await asyncio.gather(
            retrieve(decision.rag_query or english_query, history),
            execute_tool(decision.tool_name, decision.tool_params or {}, user_token),
            return_exceptions=True,
        )
        context = results[0] if not isinstance(results[0], Exception) else []
        tool_result = results[1] if not isinstance(results[1], Exception) else None
        if tool_result is not None:
            tool_result = transform_tool_result(decision.tool_name, tool_result)
        retrieved_chunks = len(context) if context else 0

        t0 = time.perf_counter()
        answer = await generate(
            query=english_query,
            context=context,
            history=history,
            tool_context=tool_result,
            language=decision.language
        )
        logger.info("BOTH response generated", extra={"user_id": user_id, "chunks_used": retrieved_chunks, "tool": decision.tool_name, "duration_s": round(time.perf_counter() - t0, 2)})

        if context:
            citations = build_citations(answer, context)

    if not answer:
        answer = "I don't have enough information to answer that question."
    
    answer = await from_english(answer, decision.language)

    if not requires_confirmation:
        history.append({"role": "user", "content": english_query})
        history.append({"role": "assistant", "content": answer})
        await set_history(user_id=user_id, session_id=req.session_id, history=history)

    response_time_ms = int((time.monotonic() - start_time) * 1000)
    logger.info("request complete", extra={
        "user_id": user_id,
        "intent": decision.intent,
        "cache_hit": cache_hit,
        "retrieved_chunks": retrieved_chunks,
        "response_time_ms": response_time_ms,
    })

    db.add(QueryEvent(
        user_id=user_id,
        session_id=req.session_id,
        query=req.query,
        cache_hit=cache_hit,
        retrieved_chunks=retrieved_chunks,
        response_time_ms=response_time_ms,
    ))
    db.add(AgentLog(
        user_id=user_id,
        username=current_user["username"],
        session_id=req.session_id,
        query=req.query,
        intent=decision.intent,
        router_decision=decision.model_dump(),
        tool_name=decision.tool_name,
        tool_params=decision.tool_params,
        tool_response=tool_result if isinstance(tool_result, dict) else None,
        maker_checker_status="pending" if requires_confirmation else None,
    ))
    await db.commit()
    
    return QueryResponse(
        answer=answer,
        citations=citations,
        requires_confirmation=requires_confirmation,
        pending_action_id=pending_action_id,
        confirmation_payload=confirmation_payload,
    )


@router.post("/confirm", response_model=QueryResponse)
async def confirm(
    req: ConfirmRequest,
    request: Request,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user["sub"]
    user_token = request.headers.get("Authorization", "").split(" ")[1]

    payload = await get_pending(session_id=req.session_id, action_id=req.action_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Pending action not found or expired.")

    await delete_pending(session_id=req.session_id, action_id=req.action_id)

    tool_result = None
    maker_checker_status = "rejected"

    if req.confirmed:
        maker_checker_status = "approved"
        try:
            tool_result = await execute_tool(
                payload["tool_name"], payload["tool_params"], user_token
            )
            answer = await generate(
                query=payload["query"],
                context=[],
                history=[],
                tool_context=tool_result,
            )
        except ToolCallError:
            answer = "The action failed to execute. Please try again later."
    else:
        answer = "Action cancelled. Let me know if you need anything else."

    history = await get_history(user_id=user_id, session_id=req.session_id) or []
    history.append({"role": "user", "content": payload["query"]})
    history.append({"role": "assistant", "content": answer})
    await set_history(user_id=user_id, session_id=req.session_id, history=history)

    db.add(AgentLog(
        user_id=user_id,
        username=current_user["username"],
        session_id=req.session_id,
        query=payload["query"],
        intent="TOOL",
        router_decision=None,
        tool_name=payload["tool_name"],
        tool_params=payload["tool_params"],
        tool_response=tool_result if isinstance(tool_result, dict) else None,
        maker_checker_status=maker_checker_status,
    ))
    await db.commit()

    return QueryResponse(answer=answer, citations=[])
