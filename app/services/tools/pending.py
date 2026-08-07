from app.services.retrieval.cache import redis
import json

PENDING_PREFIX = "pending:"

async def set_pending(session_id: str, action_id: str, payload: dict):
    key = PENDING_PREFIX + f"{session_id}:{action_id}"
    await redis.set(key, json.dumps(payload), ex=300)

async def get_pending(session_id: str, action_id: str) -> dict | None:
    key = PENDING_PREFIX + f"{session_id}:{action_id}"
    result = await redis.get(key)

    if result:
        return json.loads(result)
    else:
        return None

async def delete_pending(session_id: str, action_id: str):
    key = PENDING_PREFIX + f"{session_id}:{action_id}"
    return await redis.delete(key)