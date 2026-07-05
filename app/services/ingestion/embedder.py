from sentence_transformers import SentenceTransformer
from app.core.config import settings
import asyncio

embedder = SentenceTransformer(settings.embedding_model)

async def embed_document(text: str) -> list[float]:
    return await asyncio.to_thread(lambda: embedder.encode(text).tolist())

async def embed_query(text: str) -> list[float]:
    return await asyncio.to_thread(lambda: embedder.encode("Represent this sentence for searching relevant passages: " + text).tolist())

async def embed_batch(texts: list[str]) -> list[list[float]]:
    return await asyncio.to_thread(lambda: embedder.encode(texts).tolist())

def tokenize(text: str) -> list[str]:
    return text.lower().split()