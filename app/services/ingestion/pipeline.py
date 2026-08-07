from app.services.ingestion.parser import parse_document
from app.services.ingestion.chunker import chunk_document
from app.models.document import Document
from app.services.ingestion.embedder import embed_document, tokenize
from app.services.ingestion.storer import store_chunk, ensure_collection
from app.services.ingestion.image_optimizer import optimise_image
from app.services.ingestion.vlm import caption_image
from app.services.retrieval.cache import invalidate_answers
from app.core.logging import logging

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def run_pipeline(doc_id: str, file_path: str, db: AsyncSession) -> None:
    
    try:
        await ensure_collection()

        print(f"\n[pipeline] ── PARSE ──────────────────────────────")  # debug
        result = await parse_document(file_path)
        print(f"[pipeline] parse result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")  # debug
        print(f"[pipeline] parse result preview: {str(result)[:500]}")  # debug

        print(f"\n[pipeline] ── CHUNK ──────────────────────────────")  # debug
        chunks = chunk_document(doc_id, result)
        print(f"[pipeline] total chunks: {len(chunks)}")  # debug
        for i, chunk in enumerate(chunks):
            print(f"[pipeline] chunk[{i}] type={chunk.get('type')} content_preview={str(chunk.get('content', ''))[:100]}")  # debug

        text_n_table_chunks = []
        image_chunks = []

        for chunk in chunks:
            if chunk["type"] == "text" or chunk["type"] == "table":
                text_n_table_chunks.append(chunk)
            else:
                image_chunks.append(chunk)

        print(f"[pipeline] text/table chunks: {len(text_n_table_chunks)} | image chunks: {len(image_chunks)}")  # debug

        async def text_and_table_tracker():
            for i, chunk in enumerate(text_n_table_chunks):
                print(f"\n[pipeline] ── EMBED text/table [{i}] ───────────────")  # debug
                print(f"[pipeline] content preview: {chunk['content'][:150]}")  # debug
                dense = await embed_document(chunk["content"])
                print(f"[pipeline] dense vector: dim={len(dense)} first_5={dense[:5]}")  # debug
                tokens = tokenize(chunk["content"])
                print(f"[pipeline] sparse tokens: {len(tokens)} terms | top_5={tokens[:5]}")  # debug
                await store_chunk(chunk, dense, tokens)
                print(f"[pipeline] stored chunk [{i}]")  # debug

        async def image_tracker():
            for i, chunk in enumerate(image_chunks):
                print(f"\n[pipeline] ── IMAGE [{i}] ────────────────────────")  # debug
                if chunk["image_bytes"]:
                    print(f"[pipeline] optimising image bytes={len(chunk['image_bytes'])}")  # debug
                    b64 = await optimise_image(chunk["image_bytes"])
                    print(f"[pipeline] captioning image")  # debug
                    caption = await caption_image(b64)
                    print(f"[pipeline] caption: {caption}")  # debug
                    chunk["content"] = caption["caption"]
                    chunk["image_bytes"] = b64
                dense = await embed_document(chunk["content"])
                print(f"[pipeline] image dense vector: dim={len(dense)} first_5={dense[:5]}")  # debug
                tokens = tokenize(chunk["content"])
                print(f"[pipeline] image sparse tokens: {len(tokens)} terms")  # debug
                await store_chunk(chunk, dense, tokens)
                print(f"[pipeline] stored image chunk [{i}]")  # debug


        await asyncio.gather(text_and_table_tracker(), image_tracker())

        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()
        await invalidate_answers()
        doc.status = "completed"
        doc.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        import traceback
        print(f"[pipeline] EXCEPTION: {e}")  # debug
        print(f"[pipeline] TRACEBACK:\n{traceback.format_exc()}")  # debug
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()

        if doc:
            doc.status = "failed"
            doc.error_message = str(e)
            await db.commit()