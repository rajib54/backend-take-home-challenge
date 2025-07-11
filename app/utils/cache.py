from app.config import REDIS_HOST, REDIS_PORT
import redis.asyncio as redis
import json
from typing import Optional, Any

client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

async def get_cache(key: str) -> Optional[Any]:
    """Retrieve a cached value by key, deserializing if needed."""
    value = await client.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value

async def set_cache(key: str, value: Any, ttl: int = 3600) -> None:
    """Set a value in cache, serializing to JSON if needed."""
    try:
        serialized = json.dumps(value)
    except (TypeError, ValueError):
        serialized = str(value)
    await client.setex(key, ttl, serialized)

async def delete_cache(key: str) -> None:
    """Delete a key from the cache."""
    exists = await client.get(key)
    if exists:
        await client.delete(key)
