from app.core.config import settings
from app.services.retrieval.searcher import hybrid_search
from app.services.retrieval.fusion import fuse
from app.services.retrieval.assembler import assemble
from app.services.retrieval.reranker import rerank
from app.services.ingestion.embedder import embed_query, tokenize
from app.services.retrieval.cache import get_embedding, set_embedding
from app.services.retrieval.cache import set_retrieval, get_retrieval
from app.core.logging import get_logger

import time

logger = get_logger(__name__)

async def retrieve(query: str, history: list[dict]) -> list[dict] | None:

    logger.info("retrieve started", extra={"query": query[:100]})

    t0 = time.perf_counter()
    # L2 cache check
    query_vector = await get_embedding(query)
    if not query_vector:
        query_vector = await embed_query(query)
        await set_embedding(query, query_vector)
    logger.debug("embed complete", extra={"query": query[:100], "duration_s": round(time.perf_counter() - t0, 2)})

    t0 = time.perf_counter()
    query_tokens = tokenize(query)

    # L3 cache check
    retrieval_cache = await get_retrieval(query)

    if retrieval_cache:
        result = retrieval_cache
        logger.info("L3 cache hit", extra={"query": query[:100], "duration_s": round(time.perf_counter() - t0, 2), "chunks": len(result)})

    else:
        dense, sparse = await hybrid_search(query_vector, query_tokens, top_k=settings.top_k_chunks)
        result = fuse(sparse_results=sparse, dense_results=dense, threshold=settings.retrieval_threshold)
        logger.info("search and fuse complete", extra={
            "query": query[:100],
            "duration_s": round(time.perf_counter() - t0, 2),
            "fused_chunks": len(result),
        })

        if not result:
            logger.info("no chunks above threshold", extra={"query": query[:100]})
            return None

        await set_retrieval(query, result)

    t0 = time.perf_counter()
    result = await rerank(query, result)
    logger.debug("rerank complete", extra={"query": query[:100], "duration_s": round(time.perf_counter() - t0, 2), "chunks": len(result)})

    t0 = time.perf_counter()
    assembled = await assemble(result)
    logger.debug("assemble complete", extra={"query": query[:100], "duration_s": round(time.perf_counter() - t0, 2), "assembled": len(assembled)})

    logger.info("retrieve complete", extra={"query": query[:100], "final_chunks": len(assembled)})

    return assembled