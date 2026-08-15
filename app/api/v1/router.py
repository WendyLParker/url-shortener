from fastapi import APIRouter

from app.api.v1.endpoints import analytics, health, redirect, shorten

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(shorten.router, tags=["urls"])
api_router.include_router(analytics.router, tags=["urls"])
# The catch-all "/{short_code}" route must be registered last so it doesn't
# shadow other single-segment GET routes (e.g. /health).
api_router.include_router(redirect.router, tags=["urls"])
