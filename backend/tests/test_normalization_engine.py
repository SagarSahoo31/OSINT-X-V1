"""Tests for Normalization engine, Canonicalizer, and Deduplicator."""

import pytest
from app.collectors.base import StandardizedFinding
from app.core.constants import EntityType, FindingSeverity, FindingType
from app.normalization.canonicalizer import Canonicalizer
from app.normalization.deduplicator import Deduplicator
from app.normalization.engine import NormalizationEngine
from app.schemas.entity import EntityCreate


def test_canonicalizer_domain():
    """Test domain canonicalization and root domain extraction."""
    norm, disp, meta = Canonicalizer.canonicalize("HTTPS://Auth.Portal.Corp.Co.Uk:8443/login", EntityType.DOMAIN)
    assert norm == "auth.portal.corp.co.uk"
    assert meta["registered_domain"] == "corp.co.uk"
    assert meta["subdomain"] == "auth.portal"
    assert meta["is_subdomain"] is True


def test_canonicalizer_email():
    """Test email case folding."""
    norm, disp, meta = Canonicalizer.canonicalize("  Lead.Analyst@DEFENSE.ORG  ", EntityType.EMAIL)
    assert norm == "lead.analyst@defense.org"
    assert meta["domain"] == "defense.org"


def test_deduplicator_corroboration_boost():
    """Test that multiple independent sources boost entity confidence."""
    e1 = EntityCreate(
        investigation_id="inv-1",
        entity_type=EntityType.USERNAME,
        normalized_value="target_user",
        display_value="target_user",
        confidence=80.0,
        source_provenance=[{"tool": "holehe", "confidence": 80.0}],
    )
    e2 = EntityCreate(
        investigation_id="inv-1",
        entity_type=EntityType.USERNAME,
        normalized_value="target_user",
        display_value="target_user",
        confidence=85.0,
        source_provenance=[{"tool": "maigret", "confidence": 85.0}],
    )

    deduped = Deduplicator.deduplicate_entities([e1, e2])
    assert len(deduped) == 1
    result = deduped[0]
    assert result.confidence == 100.0  # 85.0 + 15.0 boost
    assert len(result.source_provenance) == 2


def test_normalization_engine_process():
    """Test full processing of standardized findings into entities and finding models."""
    finding1 = StandardizedFinding(
        source="holehe",
        entity_type="EMAIL",
        value="test@target.com",
        finding_type=FindingType.ACCOUNT_PRESENCE,
        severity=FindingSeverity.LOW,
        title="GitHub Account",
        confidence=90.0,
    )
    finding2 = StandardizedFinding(
        source="maigret",
        entity_type="USERNAME",
        value="test_user",
        finding_type=FindingType.ACCOUNT_PRESENCE,
        severity=FindingSeverity.LOW,
        title="Twitter Account",
        confidence=92.0,
    )

    entities, findings = NormalizationEngine.process_findings("inv-123", [finding1, finding2])
    assert len(entities) == 2
    assert len(findings) == 2

    email_entity = next(e for e in entities if e.entity_type == EntityType.EMAIL)
    assert email_entity.normalized_value == "test@target.com"
    assert len(email_entity.source_provenance) == 1
