from app.services.ingestion.parser import parse_document
from app.services.ingestion.chunker import chunk_document
from app.models.document import Document
from app.services.ingestion.embedder import embed_document, tokenize
from app.services.ingestion.storer import store_chunk, ensure_collection
from app.services.ingestion.image_optimizer import optimise_image
from app.services.ingestion.vlm import caption_image
from app.services.retrieval.cache import invalidate_answers

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

async def run_pipeline(doc_id: str, file_path: str, db: AsyncSession) -> None:
    
    try:
        await ensure_collection()
        
        result = await parse_document(file_path)
        chunks = chunk_document(doc_id, result)

        text_n_table_chunks = []
        image_chunks = []

        for chunk in chunks:
            if chunk["type"] == "text" or chunk["type"] == "table":
                text_n_table_chunks.append(chunk)
            else:
                image_chunks.append(chunk)

        async def text_and_table_tracker():
            for chunk in text_n_table_chunks:
                dense = await embed_document(chunk["content"])
                tokens = tokenize(chunk["content"])
                await store_chunk(chunk, dense, tokens)

        async def image_tracker():
            for chunk in image_chunks:
                if chunk["image_bytes"]:
                    b64 = await optimise_image(chunk["image_bytes"])
                    caption = await caption_image(b64)
                    chunk["content"] = caption["caption"]
                    chunk["image_bytes"] = b64
                dense = await embed_document(chunk["content"])
                tokens = tokenize(chunk["content"])
                await store_chunk(chunk, dense, tokens)


        await asyncio.gather(text_and_table_tracker(), image_tracker())

        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()
        await invalidate_answers()
        doc.status = "completed"
        doc.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()

        if doc:
            doc.status = "failed"
            doc.error_message = str(e)
            await db.commit()