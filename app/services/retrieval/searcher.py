from qdrant_client import AsyncQdrantClient
from qdrant_client.models import SparseVector, NamedSparseVector
from collections import Counter
import asyncio

from app.core.config import settings
from app.services.ingestion.embedder import embed_query, tokenize
from app.services.retrieval.cache import get_embedding, set_embedding

client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

async def dense_search(query_vector: list[float], top_k: int) -> list:
    
    return await client.search(
        collection_name=settings.qdrant_collection,
        query_vector=("dense", query_vector),
        limit=top_k
    )

async def sparse_search(query_tokens: list[str], top_k: int):
    counts = Counter(query_tokens)

    return await client.search(
        collection_name=settings.qdrant_collection,
        query_vector=NamedSparseVector(
            name="sparse",
            vector=SparseVector(indices=[hash(word) % (2**31) for word in counts.keys()], values=[float(count) for count in counts.values()])
        ),
        limit=top_k
    )

async def hybrid_search(query: str, top_k: int):
    query_vector = await get_embedding(query)

    if not query_vector:
        query_vector = await embed_query(query)
        await set_embedding(query, query_vector)

    query_tokens = tokenize(query)

    dense_results, sparse_results = await asyncio.gather(
        dense_search(query_vector, top_k),
        sparse_search(query_tokens, top_k)
    )
    
    return (dense_results, sparse_results)