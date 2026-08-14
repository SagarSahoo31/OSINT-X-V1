"""Investigation lifecycle and collector job models."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CollectorJobStatus, CollectorName, InvestigationStatus, TargetType
from app.models.base import Base, JSONBType, TimestampMixin, UUIDPrimaryKeyMixin


class Investigation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Core investigation entity tracking scan target, lifecycle, and authorization."""

    __tablename__ = "investigations"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_input: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    target_type: Mapped[TargetType] = mapped_column(
        Enum(TargetType, name="target_type_enum", create_type=False),
        nullable=False,
        index=True,
    )
    is_authorized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    authorization_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[InvestigationStatus] = mapped_column(
        Enum(InvestigationStatus, name="investigation_status_enum", create_type=False),
        default=InvestigationStatus.CREATED,
        nullable=False,
        index=True,
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_info: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="investigations")
    collector_jobs: Mapped[List["CollectorJob"]] = relationship(
        "CollectorJob",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    entities: Mapped[List["Entity"]] = relationship(
        "Entity",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    risk_scores: Mapped[List["RiskScore"]] = relationship(
        "RiskScore",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )


class CollectorJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks the execution state of an individual OSINT collector task."""

    __tablename__ = "collector_jobs"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    collector_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[CollectorJobStatus] = mapped_column(
        Enum(CollectorJobStatus, name="collector_job_status_enum", create_type=False),
        default=CollectorJobStatus.PENDING,
        nullable=False,
        index=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    items_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="collector_jobs")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        back_populates="collector_job",
        cascade="all, delete-orphan",
    )


Index("ix_collector_jobs_inv_collector", CollectorJob.investigation_id, CollectorJob.collector_name)
