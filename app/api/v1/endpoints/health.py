from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession, RedisClient
from app.schemas.health import HealthCheck, ServiceStatus

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check(db: DbSession, redis: RedisClient) -> HealthCheck:
    """Report the status of the API and its dependencies (Postgres, Redis)."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"

    try:
        await redis.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "unavailable"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return HealthCheck(
        status=overall,
        services=ServiceStatus(database=db_status, redis=redis_status),
    )
