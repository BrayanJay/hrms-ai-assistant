from sentence_transformers import CrossEncoder
import asyncio
from app.core.logging import get_logger

logger = get_logger(__name__)

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

async def rerank(query: str, chunks: list[dict]) -> list[dict]:
    pairs = [(query, chunk["content"]) for chunk in chunks]
    scores = await asyncio.to_thread(model.predict, pairs)

    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)

    logger.debug("rerank complete", extra={
        "query": query[:100],
        "top_chunk": ranked[0][1].get("chunk_id") if ranked else None,
        "top_score": round(float(ranked[0][0]), 4) if ranked else None,
        "scores": [
            {"chunk_id": c.get("chunk_id"), "score": round(float(s), 4)}
            for s, c in zip(scores, chunks)
        ],
    })

    return [chunk for _, chunk in ranked]