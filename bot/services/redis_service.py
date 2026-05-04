import redis.asyncio as redis
import json
from typing import Any, Optional

# --- Redis connection (singleton style) ---
_redis = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis(
            host="localhost",
            port=6379,
            db=13,
            decode_responses=True
        )
    return _redis


# --- Key builder ---
def _user_state_key(user_id: int) -> str:
    return f"user:{user_id}:state"


def _user_data_key(user_id: int) -> str:
    return f"user:{user_id}:data"


# --- Public API ---

async def set_user_state(user_id: int, state: str) -> None:
    """
    Set user state in Redis.
    """
    r = await get_redis()
    await r.set(_user_state_key(user_id), state)


async def get_user_state(user_id: int) -> Optional[str]:
    """
    Get user state from Redis.
    Returns None if not set.
    """
    r = await get_redis()
    return await r.get(_user_state_key(user_id))


async def clear_user_state(user_id: int) -> None:
    """
    Remove user state from Redis.
    """
    r = await get_redis()
    await r.delete(_user_state_key(user_id))


async def get_user_data(user_id: int) -> dict:
    r = await get_redis()
    data = await r.get(_user_data_key(user_id))

    if not data:
        return {}

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}


async def set_user_data(user_id: int, data: dict, ttl: int | None = None) -> None:
    r = await get_redis()
    value = json.dumps(data)

    if ttl is None:
        await r.set(_user_data_key(user_id), value)
    else:
        await r.set(_user_data_key(user_id), value, ex=ttl)


async def set_user_data_field(
    user_id: int,
    field: str,
    value: Any,
    ttl: int | None = None
) -> None:
    data = await get_user_data(user_id)
    data[field] = value
    await set_user_data(user_id, data, ttl=ttl)


async def get_user_data_field(user_id: int, field: str, default: Any = None) -> Any:
    """
    Get a single field from user JSON data.
    Returns default if field doesn't exist.
    """
    data = await get_user_data(user_id)
    return data.get(field, default)


async def delete_user_data_field(user_id: int, field: str) -> None:
    data = await get_user_data(user_id)

    if field in data:
        del data[field]
        await set_user_data(user_id, data)