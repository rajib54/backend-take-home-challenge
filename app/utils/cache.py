from app.config import REDIS_HOST, REDIS_PORT
import redis
import json
from typing import Optional, Any

client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def get_cache(key: str) -> Optional[Any]:
    """Retrieve a cached value by key, deserializing if needed."""
    value = client.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value

def set_cache(key: str, value: Any, ttl: int = 3600) -> None:
    """Set a value in cache, serializing to JSON if needed."""
    try:
        serialized = json.dumps(value)
    except (TypeError, ValueError):
        serialized = str(value)
    client.setex(key, ttl, serialized)

def delete_cache(key: str) -> None:
    """Delete a key from the cache."""
    if client.get(key):
        client.delete(key)
