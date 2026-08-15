from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models. Import all models in app/models/__init__.py
    so Alembic autogenerate can discover them via this metadata."""
