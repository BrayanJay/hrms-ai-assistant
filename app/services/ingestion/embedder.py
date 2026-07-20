from sentence_transformers import SentenceTransformer
from app.core.config import settings
import asyncio

_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model

async def embed_document(text: str) -> list[float]:
    return await asyncio.to_thread(lambda: get_model().encode(text).tolist())

async def embed_query(text: str) -> list[float]:
    return await asyncio.to_thread(lambda: get_model().encode("Represent this sentence for searching relevant passages: " + text).tolist())

async def embed_batch(texts: list[str]) -> list[list[float]]:
    return await asyncio.to_thread(lambda: get_model().encode(texts).tolist())

def tokenize(text: str) -> list[str]:
    return text.lower().split()