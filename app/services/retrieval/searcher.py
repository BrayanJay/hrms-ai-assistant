from qdrant_client import AsyncQdrantClient
from qdrant_client.models import SparseVector
from collections import Counter
import asyncio

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

async def dense_search(query_vector: list[float], top_k: int) -> list:
    response = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        using="dense",
        limit=top_k
    )
    return response.points

async def sparse_search(query_tokens: list[str], top_k: int) -> list:
    counts = Counter(query_tokens)
    response = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=SparseVector(
            indices=[hash(word) % (2**31) for word in counts.keys()],
            values=[float(count) for count in counts.values()]
        ),
        using="sparse",
        limit=top_k
    )
    return response.points

async def hybrid_search(query_vector: list[float], query_tokens: list[str], top_k: int):

    dense_results, sparse_results = await asyncio.gather(
        dense_search(query_vector, top_k),
        sparse_search(query_tokens, top_k)
    )

    logger.debug("hybrid search complete", extra={
        "dense_hits": len(dense_results),
        "sparse_hits": len(sparse_results),
        "dense": [
            {"chunk_id": r.payload.get("chunk_id"), "score": round(r.score, 4), "preview": r.payload.get("content", "")[:80]}
            for r in dense_results
        ],
        "sparse": [
            {"chunk_id": r.payload.get("chunk_id"), "score": round(r.score, 4), "preview": r.payload.get("content", "")[:80]}
            for r in sparse_results
        ],
    })

    return (dense_results, sparse_results)