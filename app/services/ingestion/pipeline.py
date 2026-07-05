from app.services.ingestion.parser import parse_document
from app.services.ingestion.chunker import chunk_document
from app.models.document import Document

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

async def run_pipeline(doc_id: str, file_path: str, db: AsyncSession) -> None:

    try:
        result = await parse_document(file_path)
        chunks = chunk_document(doc_id, result)

        text_n_table_chunks = []
        image_chunks = []

        for chunk in chunks:
            if chunk["type"] == "text" or chunk["type"] == "table":
                text_n_table_chunks.append(chunk)
            else:
                image_chunks.append(chunk)

        async def tracker_1():
            # embed and store text/table chunks
            pass

        async def tracker_2():
            # optimize images → VLM caption → embed → store
            pass

        await asyncio.gather(tracker_1(), tracker_2())

        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()
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