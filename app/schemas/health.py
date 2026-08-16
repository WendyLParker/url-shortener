from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Per-dependency status, each either "ok" or "unavailable"."""

    database: str = Field(description='Postgres status: "ok" or "unavailable".')
    redis: str = Field(description='Redis status: "ok" or "unavailable".')


class HealthCheck(BaseModel):
    """Response body for GET /health."""

    status: str = Field(description='Overall status: "ok" or "degraded".')
    services: ServiceStatus
