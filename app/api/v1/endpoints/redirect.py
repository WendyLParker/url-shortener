from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.api.deps import DbSession, RedisClient
from app.services.url_shortener import increment_click_count, resolve_short_code

router = APIRouter()


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str, db: DbSession, redis: RedisClient
) -> RedirectResponse:
    """
    Resolve a short code and redirect to the original URL.

    Note: Testing this endpoint from the Swagger UI often fails due to browser CORS/redirect restrictions.
    Please test it by opening the short URL directly in a browser or with:
    curl -v http://localhost:8000/api/v1/{short_code}
    """
    original_url = await resolve_short_code(db, redis, short_code)
    if original_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    await increment_click_count(db, short_code)
    return RedirectResponse(url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
