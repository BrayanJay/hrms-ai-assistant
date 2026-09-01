from app.services.ingestion.parser import parse_document
from app.services.ingestion.chunker import chunk_document
from app.models.document import Document
from app.services.ingestion.embedder import embed_document, tokenize
from app.services.ingestion.storer import store_chunk, ensure_collection
from app.services.ingestion.image_optimizer import optimise_image
from app.services.ingestion.vlm import caption_image
from app.services.retrieval.cache import invalidate_answers
from app.core.logging import get_logger

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

logger = get_logger(__name__)

async def run_pipeline(doc_id: str, file_path: str, db: AsyncSession) -> None:

    try:
        await ensure_collection()

        logger.info("pipeline started", extra={"doc_id": doc_id, "file_path": file_path})

        result = await parse_document(file_path)
        logger.info("parse complete", extra={
            "doc_id": doc_id,
            "sections": list(result.keys()) if isinstance(result, dict) else str(type(result)),
            "text_count": len(result.get("text_contents", [])),
            "table_count": len(result.get("table_contents", [])),
            "image_count": len(result.get("image_contents", [])),
        })

        doc_result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = doc_result.scalar_one_or_none()
        doc_name = doc.original_filename if doc else "Unknown"

        chunks = chunk_document(doc_id, doc_name, result)
        logger.info("chunking complete", extra={"doc_id": doc_id, "total_chunks": len(chunks)})

        for chunk in chunks:
            logger.debug("chunk created", extra={
                "doc_id": doc_id,
                "chunk_id": chunk.get("chunk_id"),
                "type": chunk.get("type"),
                "content_preview": str(chunk.get("content", ""))[:100],
            })

        text_n_table_chunks = []
        image_chunks = []

        for chunk in chunks:
            if chunk["type"] == "text" or chunk["type"] == "table":
                text_n_table_chunks.append(chunk)
            else:
                image_chunks.append(chunk)

        logger.info("chunk split", extra={
            "doc_id": doc_id,
            "text_table_chunks": len(text_n_table_chunks),
            "image_chunks": len(image_chunks),
        })

        async def embed_text_and_tables():
            for i, chunk in enumerate(text_n_table_chunks):
                dense = await embed_document(chunk["content"])
                tokens = tokenize(chunk["content"])
                await store_chunk(chunk, dense, tokens)
                logger.debug("text/table chunk embedded and stored", extra={
                    "doc_id": doc_id,
                    "index": i,
                    "chunk_id": chunk.get("chunk_id"),
                    "vector_dim": len(dense),
                    "sparse_terms": len(tokens),
                })

        async def embed_images():
            for i, chunk in enumerate(image_chunks):
                if chunk["image_bytes"]:
                    b64 = await optimise_image(chunk["image_bytes"])
                    caption = await caption_image(b64)
                    logger.debug("image captioned", extra={
                        "doc_id": doc_id,
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                        "caption_type": caption.get("type"),
                        "caption_preview": caption.get("caption", "")[:100],
                    })
                    chunk["content"] = caption["caption"]
                    chunk["image_bytes"] = b64

                if not chunk["content"]:
                    logger.debug("image chunk skipped — no caption", extra={"doc_id": doc_id, "index": i})
                    continue

                dense = await embed_document(chunk["content"])
                tokens = tokenize(chunk["content"])
                await store_chunk(chunk, dense, tokens)
                logger.debug("image chunk embedded and stored", extra={
                    "doc_id": doc_id,
                    "index": i,
                    "chunk_id": chunk.get("chunk_id"),
                    "vector_dim": len(dense),
                    "sparse_terms": len(tokens),
                })

        await asyncio.gather(embed_text_and_tables(), embed_images())

        await invalidate_answers()
        doc.status = "completed"
        doc.completed_at = datetime.now(timezone.utc)
        await db.commit()

        logger.info("pipeline complete", extra={"doc_id": doc_id, "doc_name": doc_name, "status": "completed"})

    except Exception as e:
        logger.exception("pipeline failed", extra={"doc_id": doc_id, "error": str(e)})
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()

        if doc:
            doc.status = "failed"
            doc.error_message = str(e)
            await db.commit()