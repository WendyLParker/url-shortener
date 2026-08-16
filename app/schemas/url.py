from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ShortenRequest(BaseModel):
    """Request body for POST /shorten."""

    original_url: HttpUrl = Field(description="The long URL to shorten.")


class ShortenResponse(BaseModel):
    """Response body for POST /shorten."""

    model_config = ConfigDict(from_attributes=True)

    short_code: str = Field(description="The generated short code.")
    short_url: str = Field(description="The full short URL to share.")
    original_url: str = Field(description="The original long URL.")
    created_at: datetime = Field(description="When the short URL was created.")


class URLAnalytics(BaseModel):
    """Response body for GET /analytics/{short_code}."""

    model_config = ConfigDict(from_attributes=True)

    short_code: str = Field(description="The short code these analytics belong to.")
    original_url: str = Field(description="The original long URL.")
    click_count: int = Field(description="Number of times the short URL has been visited.")
    created_at: datetime = Field(description="When the short URL was created.")
