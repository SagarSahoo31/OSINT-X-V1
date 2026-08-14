"""Risk scoring model representing explainable exposure risk calculations."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JSONBType, TimestampMixin, UUIDPrimaryKeyMixin


class RiskScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Calculated OSINT-X Exposure Risk Score and factor decomposition."""

    __tablename__ = "risk_scores"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    severity_score: Mapped[float] = mapped_column(Float, nullable=False)
    exposure_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_weight: Mapped[float] = mapped_column(Float, nullable=False)
    factors: Mapped[Dict[str, Any]] = mapped_column(JSONBType, default=dict, nullable=False)
    explanation: Mapped[List[str]] = mapped_column(JSONBType, default=list, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="risk_scores")


Index("ix_risk_scores_inv_calc", RiskScore.investigation_id, RiskScore.calculated_at)
