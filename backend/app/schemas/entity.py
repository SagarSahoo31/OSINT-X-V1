"""Pydantic schemas for Entities and Relationships."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import EntityType, RelationshipType


class EntityBase(BaseModel):
    """Base attributes for an intelligence entity."""
    entity_type: EntityType
    normalized_value: str
    display_value: str
    confidence: float = Field(default=100.0, ge=0.0, le=100.0)
    meta_info: Dict[str, Any] = Field(default_factory=dict)
    source_provenance: List[Dict[str, Any]] = Field(default_factory=list)


class EntityCreate(EntityBase):
    """Schema for persisting a discovered entity."""
    investigation_id: str
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class EntityRead(EntityBase):
    """Schema for returning entity data."""
    id: str
    investigation_id: str
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RelationshipBase(BaseModel):
    """Base attributes for an explainable relationship."""
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    confidence: float = Field(default=80.0, ge=0.0, le=100.0)
    reason: str = Field(..., max_length=500)
    source_tool: str = Field(..., max_length=50)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class RelationshipCreate(RelationshipBase):
    """Schema for persisting a relationship."""
    investigation_id: str
    discovered_at: Optional[datetime] = None


class RelationshipRead(RelationshipBase):
    """Schema for returning relationship data."""
    id: str
    investigation_id: str
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GraphNode(BaseModel):
    """Graph projection node formatted for React Flow or Cytoscape.js."""
    id: str
    label: str
    entity_type: EntityType
    confidence: float
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Graph projection edge formatted for React Flow or Cytoscape.js."""
    id: str
    source: str
    target: str
    label: RelationshipType
    confidence: float
    reason: str
    source_tool: str


class GraphData(BaseModel):
    """Complete graph projection payload."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
