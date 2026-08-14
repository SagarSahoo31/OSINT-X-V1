"""Pydantic schemas for Exposure Risk calculations."""

from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class RiskFactorBreakdown(BaseModel):
    """Component weight breakdown for the OSINT-X Exposure Risk Score."""
    severity_score: float = Field(..., ge=0.0, le=100.0)
    exposure_score: float = Field(..., ge=0.0, le=100.0)
    confidence_weight: float = Field(..., ge=0.0, le=1.0)
    critical_findings_count: int = 0
    high_findings_count: int = 0
    internet_facing_assets_count: int = 0
    identity_exposure_count: int = 0


class RiskScoreRead(BaseModel):
    """Schema for returning the OSINT-X Exposure Risk Score."""
    id: str
    investigation_id: str
    overall_score: float = Field(..., ge=0.0, le=100.0, description="OSINT-X Exposure Risk Score (0-100)")
    severity_score: float = Field(..., ge=0.0, le=100.0)
    exposure_score: float = Field(..., ge=0.0, le=100.0)
    confidence_weight: float = Field(..., ge=0.0, le=1.0)
    factors: Dict[str, Any] = Field(default_factory=dict)
    explanation: List[str] = Field(default_factory=list, description="Human-readable justification reasons")
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
