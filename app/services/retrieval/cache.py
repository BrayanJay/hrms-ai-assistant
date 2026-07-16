from redis.asyncio import Redis
from app.core.config import settings
import json

redis = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True)

L1_PREFIX = "l1:answer:"
L2_PREFIX = "l2:embedding:"
L3_PREFIX = "l3:retrieval:"

async def get_answer(query: str) -> str | None:
    key = L1_PREFIX + query

    result = await redis.get(key)

    return result

async def set_answer(query: str, answer: str):
    key = L1_PREFIX + query
    await redis.set(key, answer, ex=3600)

async def get_embedding(query: str) -> list[float] | None:
    key = L2_PREFIX + query
    result = await redis.get(key)

    if result:
        return json.loads(result)
    else:
        return None
    
async def set_embedding(query: str, vector: list[float]):
    key = L2_PREFIX + query
    await redis.set(key, json.dumps(vector), ex=3600*24*7)

async def get_retrieval(query: str) -> list | None:
    key = L3_PREFIX + query
    result = await redis.get(key)
    if result:
        return json.loads(result)
    
    return None

async def set_retrieval(query: str, chunks: list):
    key = L3_PREFIX + query
    await redis.set(key, json.dumps(chunks), ex=1800)

async def invalidate_answers():
    keys = await redis.keys(L1_PREFIX + "*")
    if keys:
        await redis.delete(*keys)