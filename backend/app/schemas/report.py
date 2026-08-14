"""Pydantic schemas for Report generation and downloads."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    """Schema for requesting report generation."""
    investigation_id: str
    format: str = Field(..., pattern="^(PDF|JSON|CSV)$")
    title: Optional[str] = None
    include_evidence: bool = True
    include_raw_data: bool = False


class ReportRead(BaseModel):
    """Schema for returning generated report details."""
    id: str
    investigation_id: str
    format: str
    title: str
    file_path: str
    file_size_bytes: int
    generated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
