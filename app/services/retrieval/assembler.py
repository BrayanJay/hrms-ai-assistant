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
    seen = set()

    citation = 1
    for chunk in chunks:
        seen_key = chunk["parent_chunk_id"] or chunk["chunk_id"]
        if seen_key in seen:
            continue
        seen.add(seen_key)

        source = parent_map.get(chunk["parent_chunk_id"], chunk)
        context.append({
            "citation": citation,
            "type": source["type"],
            "content": source["content"],
            "image_bytes": source.get("image_bytes"),
            "doc_id": source.get("doc_id")
        })
        citation += 1
    
    return context

