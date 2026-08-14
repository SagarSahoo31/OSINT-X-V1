"""Finding and Evidence models storing raw and standardized collector findings."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import FindingSeverity, FindingType
from app.models.base import Base, JSONBType, TimestampMixin, UUIDPrimaryKeyMixin


class Finding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Raw or normalized security/footprint finding recorded by a collector."""

    __tablename__ = "findings"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    collector_job_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("collector_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_tool: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    finding_type: Mapped[FindingType] = mapped_column(
        Enum(FindingType, name="finding_type_enum", create_type=False),
        nullable=False,
        index=True,
    )
    severity: Mapped[FindingSeverity] = mapped_column(
        Enum(FindingSeverity, name="finding_severity_enum", create_type=False),
        default=FindingSeverity.INFO,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    normalized_data: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="findings")
    collector_job: Mapped[Optional["CollectorJob"]] = relationship("CollectorJob", back_populates="findings")
    evidence_items: Mapped[List["Evidence"]] = relationship(
        "Evidence",
        back_populates="finding",
        cascade="all, delete-orphan",
    )


class Evidence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Verifiable evidence snapshot linked to a specific finding."""

    __tablename__ = "evidence"

    finding_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    hash_digest: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    provenance_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    finding: Mapped["Finding"] = relationship("Finding", back_populates="evidence_items")


Index("ix_findings_inv_severity", Finding.investigation_id, Finding.severity)
Index("ix_findings_inv_type", Finding.investigation_id, Finding.finding_type)
