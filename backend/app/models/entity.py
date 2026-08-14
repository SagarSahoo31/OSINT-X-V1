"""Entity and Relationship models representing the canonical intelligence graph."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EntityType, RelationshipType
from app.models.base import Base, JSONBType, TimestampMixin, UUIDPrimaryKeyMixin


class Entity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Canonical entity extracted and resolved from multiple OSINT sources."""

    __tablename__ = "entities"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entity_type_enum", create_type=False),
        nullable=False,
        index=True,
    )
    normalized_value: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    display_value: Mapped[str] = mapped_column(String(500), nullable=False)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    meta_info: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    source_provenance: Mapped[List[Dict[str, Any]]] = mapped_column(JSONBType, default=list, nullable=False)

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="entities")
    outgoing_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )
    incoming_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "investigation_id", "entity_type", "normalized_value",
            name="uq_investigation_entity_type_value",
        ),
        Index("ix_entities_inv_type_val", "investigation_id", "entity_type", "normalized_value"),
    )


class Relationship(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Explainable directed relationship between two entities."""

    __tablename__ = "relationships"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType, name="relationship_type_enum", create_type=False),
        nullable=False,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, default=80.0, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    source_tool: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="relationships")
    source_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[source_entity_id], back_populates="outgoing_relationships")
    target_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[target_entity_id], back_populates="incoming_relationships")

    __table_args__ = (
        UniqueConstraint(
            "investigation_id", "source_entity_id", "target_entity_id", "relationship_type",
            name="uq_investigation_rel_src_tgt_type",
        ),
        Index("ix_rel_inv_src_tgt", "investigation_id", "source_entity_id", "target_entity_id"),
    )
