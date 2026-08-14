"""Tests for OSINT-X Exposure Risk scoring engine."""

import pytest
from app.core.constants import EntityType, FindingSeverity, FindingType
from app.schemas.entity import EntityCreate
from app.schemas.finding import FindingCreate
from app.scoring.calculator import RiskEngine


def test_empty_risk_calculation():
    """Test risk calculation on empty findings."""
    overall, sev, exp, conf, factors, reasons = RiskEngine.calculate_risk([], [], "inv-empty")
    assert overall == 0.0
    assert len(reasons) >= 1
    assert "minimal" in reasons[0]


def test_high_exposure_risk_calculation():
    """Test multi-factor risk calculation on rich finding footprint."""
    findings = [
        FindingCreate(
            investigation_id="inv-1",
            source_tool="httpx",
            finding_type=FindingType.HTTP_ENDPOINT,
            severity=FindingSeverity.HIGH,
            title="Unauthenticated Admin Endpoint",
            confidence=95.0,
        ),
        FindingCreate(
            investigation_id="inv-1",
            source_tool="whatweb",
            finding_type=FindingType.TECHNOLOGY_STACK,
            severity=FindingSeverity.MEDIUM,
            title="Outdated Web Server",
            confidence=90.0,
        ),
    ]

    entities = [
        EntityCreate(investigation_id="inv-1", entity_type=EntityType.DOMAIN, normalized_value="target.org", display_value="target.org"),
        EntityCreate(investigation_id="inv-1", entity_type=EntityType.SUBDOMAIN, normalized_value="admin.target.org", display_value="admin.target.org"),
        EntityCreate(investigation_id="inv-1", entity_type=EntityType.IP, normalized_value="198.51.100.5", display_value="198.51.100.5"),
        EntityCreate(investigation_id="inv-1", entity_type=EntityType.TECHNOLOGY, normalized_value="apache", display_value="Apache"),
    ]

    overall, sev, exp, conf, factors, reasons = RiskEngine.calculate_risk(findings, entities, "inv-1")
    assert 0.0 <= overall <= 100.0
    assert overall > 40.0  # Significant risk given HIGH finding and multiple assets
    assert factors["high_findings"] == 1
    assert any("High severity finding" in r for r in reasons)
