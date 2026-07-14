from app.core.config import settings
from qdrant_client import AsyncQdrantClient

client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

async def assemble(chunks: list[dict]) -> list[dict]:
    parent_chunk_ids = set()

    for chunk in chunks:
        if chunk["parent_chunk_id"]:
            parent_chunk_ids.add(chunk["parent_chunk_id"])

    parent_chunks = await client.retrieve(
      collection_name=settings.qdrant_collection,
      ids=[abs(hash(pid)) % (2**63) for pid in parent_chunk_ids]
    )

    parent_map = {p.payload["chunk_id"]: p.payload for p in parent_chunks}

    context = []
    for citation, chunk in enumerate(chunks, start=1):
        source = parent_map.get(chunk["parent_chunk_id"], chunk)
        context.append({
            "citation": citation,
            "type": source["type"],
            "content": source["content"],
            "image_bytes": source.get("image_bytes")
        })
    
    return context

