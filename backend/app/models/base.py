"""SQLAlchemy 2.0 Base models, UUID primary keys, and timestamp mixins."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator, JSON


class JSONBType(TypeDecorator):
    """Platform-independent JSON type that uses JSONB in PostgreSQL and JSON in SQLite."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class Base(DeclarativeBase):
    """Base declarative class for all OSINT-X SQLAlchemy models."""

    def to_dict(self) -> Dict[str, Any]:
        """Serializes model attributes to dictionary."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }


class TimestampMixin:
    """Provides created_at and updated_at timestamp columns with UTC timezone."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Provides standard UUID primary key."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
