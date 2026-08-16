from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.deps import DbSession, RedisClient
from app.schemas.health import HealthCheck, ServiceStatus

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check(response: Response, db: DbSession, redis: RedisClient) -> HealthCheck:
    """Report the status of the API and its dependencies (Postgres, Redis).

    Returns HTTP 200 when everything is reachable, or 503 when any dependency
    is unavailable, so load balancers / orchestrator health probes can act on
    the status code alone.
    """
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

    is_healthy = db_status == "ok" and redis_status == "ok"
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthCheck(
        status="ok" if is_healthy else "degraded",
        services=ServiceStatus(database=db_status, redis=redis_status),
    )
