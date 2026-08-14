"""Tests for domain constants, entity types, and relationship enums."""

from app.core.constants import (
    CollectorName,
    EntityType,
    FindingSeverity,
    FindingType,
    InvestigationStatus,
    RelationshipType,
    TargetType,
    UserRole,
)


def test_entity_types():
    """Verify core entity types defined in specification."""
    expected = {
        "PERSON",
        "EMAIL",
        "USERNAME",
        "ORGANIZATION",
        "DOMAIN",
        "SUBDOMAIN",
        "IP",
        "ASN",
        "URL",
        "CERTIFICATE",
        "SERVICE",
        "TECHNOLOGY",
        "BREACH",
        "THREAT_INDICATOR",
    }
    actual = {e.value for e in EntityType}
    assert expected == actual


def test_relationship_types():
    """Verify relationship types defined in specification."""
    expected = {
        "OWNS",
        "ASSOCIATED_WITH",
        "USES",
        "RESOLVES_TO",
        "HOSTED_ON",
        "SUBDOMAIN_OF",
        "ISSUED_TO",
        "DISCOVERED_FROM",
        "CONNECTED_TO",
        "OBSERVED_ON",
        "POSSIBLY_BELONGS_TO",
    }
    actual = {r.value for r in RelationshipType}
    assert expected == actual


def test_investigation_statuses():
    """Verify investigation status lifecycle states."""
    expected = {"CREATED", "QUEUED", "RUNNING", "PARTIAL", "COMPLETED", "FAILED", "CANCELLED"}
    actual = {s.value for s in InvestigationStatus}
    assert expected == actual


def test_target_types():
    """Verify supported target types."""
    expected = {"EMAIL", "USERNAME", "DOMAIN", "IP", "URL"}
    actual = {t.value for t in TargetType}
    assert expected == actual


def test_finding_severities():
    """Verify finding severity levels."""
    expected = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
    actual = {s.value for s in FindingSeverity}
    assert expected == actual
