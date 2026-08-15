from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.schemas.url import URLAnalytics
from app.services.url_shortener import get_short_url_by_code

router = APIRouter()


@router.get("/analytics/{short_code}", response_model=URLAnalytics)
async def get_url_analytics(short_code: str, db: DbSession) -> URLAnalytics:
    """Return click analytics for a given short code."""
    short_url = await get_short_url_by_code(db, short_code)
    if short_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    return URLAnalytics.model_validate(short_url)
