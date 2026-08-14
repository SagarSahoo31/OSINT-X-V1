"""Pydantic schemas for Investigations and Collector Jobs."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import CollectorJobStatus, InvestigationStatus, TargetType


class InvestigationCreate(BaseModel):
    """Schema for creating a new investigation."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    target_input: str = Field(..., min_length=1, max_length=500)
    target_type: TargetType
    is_authorized: bool = Field(
        ...,
        description="Explicit confirmation that scanning this target is authorized",
    )
    authorization_notes: Optional[str] = None
    enabled_collectors: Optional[List[str]] = None


class InvestigationUpdate(BaseModel):
    """Schema for updating investigation metadata."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[InvestigationStatus] = None
    is_authorized: Optional[bool] = None
    authorization_notes: Optional[str] = None


class CollectorJobRead(BaseModel):
    """Schema for returning collector job execution status."""
    id: str
    investigation_id: str
    collector_name: str
    status: CollectorJobStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    raw_output_path: Optional[str] = None
    error_message: Optional[str] = None
    items_count: int = 0
    execution_duration_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationRead(BaseModel):
    """Schema for returning full investigation details."""
    id: str
    title: str
    description: Optional[str] = None
    target_input: str
    target_type: TargetType
    is_authorized: bool
    authorization_notes: Optional[str] = None
    status: InvestigationStatus
    user_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    meta_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    collector_jobs: List[CollectorJobRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InvestigationSummary(BaseModel):
    """Schema for lightweight investigation list cards."""
    id: str
    title: str
    target_input: str
    target_type: TargetType
    status: InvestigationStatus
    is_authorized: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    entities_count: int = 0
    findings_count: int = 0
    risk_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
