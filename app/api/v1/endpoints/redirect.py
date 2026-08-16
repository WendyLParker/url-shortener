from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import RedirectResponse

from app.api.deps import DbSession, RedisClient
from app.services.url_shortener import SHORT_CODE_PATTERN, increment_click_count, resolve_short_code

router = APIRouter()


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: Annotated[str, Path(pattern=SHORT_CODE_PATTERN)],
    db: DbSession,
    redis: RedisClient,
) -> RedirectResponse:
    """Resolve a short code and redirect to its original URL, tracking a click.

    Note: Swagger UI's "Try it out" follows redirects via the browser's fetch
    API, which silently swallows the 307 response. To actually see the
    redirect, open the short URL directly in a browser tab, or run:
    `curl -i http://localhost:8000/api/v1/{short_code}`.
    """
    original_url = await resolve_short_code(db, redis, short_code)
    if original_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    await increment_click_count(db, short_code)
    return RedirectResponse(url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
