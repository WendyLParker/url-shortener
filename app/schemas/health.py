from pydantic import BaseModel


class ServiceStatus(BaseModel):
    database: str
    redis: str


class HealthCheck(BaseModel):
    status: str
    services: ServiceStatus
