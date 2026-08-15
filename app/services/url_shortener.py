import secrets
import string

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.url import ShortURL

_ALPHABET = string.ascii_letters + string.digits
_MAX_GENERATION_ATTEMPTS = 5


def _cache_key(short_code: str) -> str:
    return f"short_url:{short_code}"


def _generate_code() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(settings.SHORT_CODE_LENGTH))


async def _generate_unique_code(db: AsyncSession) -> str:
    for _ in range(_MAX_GENERATION_ATTEMPTS):
        code = _generate_code()
        exists = await db.scalar(select(ShortURL.id).where(ShortURL.short_code == code))
        if exists is None:
            return code
    raise RuntimeError("Could not generate a unique short code, please try again.")


async def create_short_url(db: AsyncSession, original_url: str) -> ShortURL:
    """Persist a new short URL with a freshly generated, unique short code."""
    short_code = await _generate_unique_code(db)
    short_url = ShortURL(short_code=short_code, original_url=original_url)
    db.add(short_url)
    await db.commit()
    await db.refresh(short_url)
    return short_url


async def cache_original_url(redis: Redis, short_code: str, original_url: str) -> None:
    await redis.set(_cache_key(short_code), original_url, ex=settings.URL_CACHE_TTL_SECONDS)


async def resolve_short_code(db: AsyncSession, redis: Redis, short_code: str) -> str | None:
    """Resolve a short code to its original URL, preferring the Redis cache
    (cache-aside: fall back to Postgres on a miss, then repopulate the cache)."""
    cached_url = await redis.get(_cache_key(short_code))
    if cached_url is not None:
        return cached_url

    short_url = await get_short_url_by_code(db, short_code)
    if short_url is None:
        return None

    await cache_original_url(redis, short_code, short_url.original_url)
    return short_url.original_url


async def increment_click_count(db: AsyncSession, short_code: str) -> None:
    """Atomically increment the click count for a short code."""
    await db.execute(
        update(ShortURL)
        .where(ShortURL.short_code == short_code)
        .values(click_count=ShortURL.click_count + 1)
    )
    await db.commit()


async def get_short_url_by_code(db: AsyncSession, short_code: str) -> ShortURL | None:
    return await db.scalar(select(ShortURL).where(ShortURL.short_code == short_code))
