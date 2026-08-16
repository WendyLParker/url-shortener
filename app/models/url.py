from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

#: Matches pydantic's HttpUrl max length, so a URL that passes request
#: validation is always guaranteed to fit in this column.
_MAX_URL_LENGTH = 2083


class ShortURL(Base):
    """A shortened URL: its code, the original destination, and click stats."""

    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(String(_MAX_URL_LENGTH), nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
