"""Pydantic schemas for Findings and Evidence captures."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import FindingSeverity, FindingType


class EvidenceBase(BaseModel):
    """Base evidence capture properties."""
    evidence_type: str
    content: Dict[str, Any] = Field(default_factory=dict)
    hash_digest: Optional[str] = None
    provenance_url: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    """Schema for creating evidence."""
    finding_id: str
    recorded_at: Optional[datetime] = None


class EvidenceRead(EvidenceBase):
    """Schema for returning evidence."""
    id: str
    finding_id: str
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FindingBase(BaseModel):
    """Base finding properties."""
    source_tool: str
    finding_type: FindingType
    severity: FindingSeverity = FindingSeverity.INFO
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    normalized_data: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=100.0, ge=0.0, le=100.0)


class FindingCreate(FindingBase):
    """Schema for saving a finding."""
    investigation_id: str
    collector_job_id: Optional[str] = None
    observed_at: Optional[datetime] = None


class FindingRead(FindingBase):
    """Schema for returning a finding with its evidence items."""
    id: str
    investigation_id: str
    collector_job_id: Optional[str] = None
    observed_at: datetime
    created_at: datetime
    updated_at: datetime
    evidence_items: List[EvidenceRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
