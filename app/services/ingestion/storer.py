from app.core.config import settings
from app.core.logging import get_logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams, PointStruct, SparseVector
from collections import Counter

logger = get_logger(__name__)

client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

async def ensure_collection() -> None:
    if not await client.collection_exists(settings.qdrant_collection):
        await client.create_collection(collection_name=settings.qdrant_collection, vectors_config={"dense": VectorParams(size=settings.embedding_dimension, distance=Distance.COSINE)}, sparse_vectors_config={"sparse": SparseVectorParams()})
        logger.info("qdrant collection created", extra={"collection": settings.qdrant_collection})

async def delete_doc_chunks(doc_id: str) -> None:
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    if not await client.collection_exists(settings.qdrant_collection):
        return
    await client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        )
    )
    logger.info("qdrant chunks deleted", extra={"doc_id": doc_id})

async def store_chunk(chunk: dict, dense_vector: list[float], tokens: list[str]) -> None:
        
    counts = Counter(tokens)
    indices = [hash(word) % (2**31) for word in counts.keys()]
    values = [float(count) for count in counts.values()]
    sparse_vector = SparseVector(indices=indices, values=values)

    point = PointStruct(
        id=abs(hash(chunk["chunk_id"])) % (2**63),
        vector={
            "dense": dense_vector,
            "sparse": sparse_vector
        },
        payload={
            "chunk_id": chunk["chunk_id"],
            "parent_chunk_id": chunk["parent_chunk_id"],
            "doc_id": chunk["doc_id"],
            "doc_name": chunk.get("doc_name"),
            "type": chunk["type"],
            "content": chunk["content"],
            "page": chunk.get("page"),
            "image_bytes": chunk.get("image_bytes"),
        }
    )

    await client.upsert(collection_name=settings.qdrant_collection, points=[point])