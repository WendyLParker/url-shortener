from fastapi import APIRouter, status

from app.api.deps import DbSession, RedisClient
from app.core.config import settings
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.url_shortener import cache_original_url, create_short_url

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(payload: ShortenRequest, db: DbSession, redis: RedisClient) -> ShortenResponse:
    """Generate a short code for a long URL, persist it, and warm the cache."""
    short_url = await create_short_url(db, str(payload.original_url))
    await cache_original_url(redis, short_url.short_code, short_url.original_url)

    return ShortenResponse(
        short_code=short_url.short_code,
        short_url=f"{settings.BASE_URL}{settings.API_V1_PREFIX}/{short_url.short_code}",
        original_url=short_url.original_url,
        created_at=short_url.created_at,
    )
