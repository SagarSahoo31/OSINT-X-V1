"""Tests for Pydantic schema validation, bounds checking, and serialization."""

import pytest
from pydantic import ValidationError

from app.core.constants import EntityType, FindingSeverity, FindingType, RelationshipType, TargetType, UserRole
from app.schemas.entity import EntityBase, GraphData, GraphEdge, GraphNode, RelationshipBase
from app.schemas.finding import FindingBase
from app.schemas.investigation import InvestigationCreate
from app.schemas.report import ReportCreate
from app.schemas.risk import RiskScoreRead
from app.schemas.user import UserCreate


def test_user_create_validation():
    """Verify password length and email validation."""
    valid_user = UserCreate(
        email="test@osintx.org",
        username="valid_user",
        password="secure_password_123",
        role=UserRole.ANALYST,
    )
    assert valid_user.email == "test@osintx.org"

    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            username="valid_user",
            password="secure_password_123",
        )

    with pytest.raises(ValidationError):
        UserCreate(
            email="test@osintx.org",
            username="valid_user",
            password="short",  # < 8 chars
        )


def test_investigation_create_authorization_requirement():
    """Verify target authorization confirmation requirement."""
    valid = InvestigationCreate(
        title="Authorized Assessment",
        target_input="target.org",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
        authorization_notes="Authorized by client",
    )
    assert valid.is_authorized is True


def test_confidence_bounds_validation():
    """Verify confidence score bounds (0.0 to 100.0)."""
    entity = EntityBase(
        entity_type=EntityType.EMAIL,
        normalized_value="user@target.com",
        display_value="user@target.com",
        confidence=95.5,
    )
    assert entity.confidence == 95.5

    with pytest.raises(ValidationError):
        EntityBase(
            entity_type=EntityType.EMAIL,
            normalized_value="user@target.com",
            display_value="user@target.com",
            confidence=105.0,  # > 100
        )

    with pytest.raises(ValidationError):
        EntityBase(
            entity_type=EntityType.EMAIL,
            normalized_value="user@target.com",
            display_value="user@target.com",
            confidence=-5.0,  # < 0
        )


def test_graph_data_schema():
    """Verify Graph projection schema."""
    node1 = GraphNode(id="n1", label="target.com", entity_type=EntityType.DOMAIN, confidence=100.0)
    node2 = GraphNode(id="n2", label="192.0.2.1", entity_type=EntityType.IP, confidence=90.0)
    edge = GraphEdge(
        id="e1",
        source="n1",
        target="n2",
        label=RelationshipType.RESOLVES_TO,
        confidence=90.0,
        reason="A Record DNS Resolution",
        source_tool="dns",
    )
    graph = GraphData(nodes=[node1, node2], edges=[edge])
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.edges[0].label == RelationshipType.RESOLVES_TO


def test_report_create_format_validation():
    """Verify report format validation accepts only PDF, JSON, CSV."""
    valid_report = ReportCreate(
        investigation_id="inv-123",
        format="PDF",
    )
    assert valid_report.format == "PDF"

    with pytest.raises(ValidationError):
        ReportCreate(
            investigation_id="inv-123",
            format="EXE",
        )
