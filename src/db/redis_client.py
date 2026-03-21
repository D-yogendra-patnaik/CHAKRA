import logging
import redis as redis_lib
from src.core.config import settings

logger = logging.getLogger("chakra")

_redis_client = None
_redis_available = None


def _get_redis():
    """Lazily connect to Redis. Returns None if unavailable."""
    global _redis_client, _redis_available
    if _redis_available is False:
        return None
    if _redis_client is None:
        try:
            _redis_client = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()
            _redis_available = True
            logger.info("Redis connected.")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}. Running without Redis.")
            _redis_available = False
            _redis_client = None
    return _redis_client


def check_rate_limit(tenant_id: str, limit: int = 100, window: int = 60) -> bool:
    """Returns True if allowed. Always allows if Redis is down."""
    client = _get_redis()
    if client is None:
        return True
    try:
        key = f"rate_limit:{tenant_id}"
        reqs = client.incr(key)
        if reqs == 1:
            client.expire(key, window)
        return reqs <= limit
    except Exception:
        return True


def store_session_context(session_id: str, context: dict):
    client = _get_redis()
    if client is None:
        return
    try:
        client.hset(f"session:{session_id}", mapping=context)
        client.expire(f"session:{session_id}", 3600)
    except Exception:
        pass
