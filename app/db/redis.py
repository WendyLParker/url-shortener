from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency that yields the shared Redis client."""
    yield redis_client
