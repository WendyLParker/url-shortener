"""Business logic for creating, resolving, and tracking short URLs.

Redis is used as a read-through cache in front of Postgres (cache-aside
pattern): lookups check Redis first and only fall back to the database on a
cache miss, repopulating the cache afterwards.
"""

import secrets
import string

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.url import ShortURL

_ALPHABET = string.ascii_letters + string.digits
_MAX_GENERATION_ATTEMPTS = 5

#: Shared pattern for validating short codes in path parameters. Matches the
#: alphabet/length used by `_generate_code`, so malformed codes are rejected
#: with a 422 before ever touching Redis or Postgres.
SHORT_CODE_PATTERN = r"^[A-Za-z0-9]{1,32}$"


class ShortCodeGenerationError(RuntimeError):
    """Raised when a unique short code could not be generated after several attempts."""


def _cache_key(short_code: str) -> str:
    return f"short_url:{short_code}"


def _generate_code() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(settings.SHORT_CODE_LENGTH))


async def create_short_url(db: AsyncSession, original_url: str) -> ShortURL:
    """Persist a new short URL under a freshly generated, unique short code.

    Generation and insertion happen together so a collision (another request
    generating the same code concurrently) is caught as a database integrity
    error and simply retried, rather than relying solely on an upfront
    existence check.
    """
    for _ in range(_MAX_GENERATION_ATTEMPTS):
        short_url = ShortURL(short_code=_generate_code(), original_url=original_url)
        db.add(short_url)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            continue
        await db.refresh(short_url)
        return short_url

    raise ShortCodeGenerationError(
        f"Could not generate a unique short code after {_MAX_GENERATION_ATTEMPTS} attempts."
    )


async def cache_original_url(redis: Redis, short_code: str, original_url: str) -> None:
    """Cache the short code -> original URL mapping with a TTL."""
    await redis.set(_cache_key(short_code), original_url, ex=settings.URL_CACHE_TTL_SECONDS)


async def resolve_short_code(db: AsyncSession, redis: Redis, short_code: str) -> str | None:
    """Resolve a short code to its original URL, preferring the Redis cache.

    Returns None if the short code does not exist.
    """
    cached_url = await redis.get(_cache_key(short_code))
    if cached_url is not None:
        return cached_url

    short_url = await get_short_url_by_code(db, short_code)
    if short_url is None:
        return None

    await cache_original_url(redis, short_code, short_url.original_url)
    return short_url.original_url


async def increment_click_count(db: AsyncSession, short_code: str) -> None:
    """Atomically increment the click count for a short code.

    Uses a single `UPDATE ... SET click_count = click_count + 1` so concurrent
    redirects can't lose increments to a read-modify-write race.
    """
    await db.execute(
        update(ShortURL)
        .where(ShortURL.short_code == short_code)
        .values(click_count=ShortURL.click_count + 1)
    )
    await db.commit()


async def get_short_url_by_code(db: AsyncSession, short_code: str) -> ShortURL | None:
    """Fetch a short URL row by its code, or None if it doesn't exist."""
    return await db.scalar(select(ShortURL).where(ShortURL.short_code == short_code))
