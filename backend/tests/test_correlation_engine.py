"""Tests for CorrelationEngine and deterministic relationship rules."""

import pytest
from app.correlation.engine import CorrelationEngine
from app.core.constants import EntityType, RelationshipType
from app.schemas.entity import EntityCreate


def test_subdomain_and_ip_correlation():
    """Test SubdomainOfRule and DomainResolvesToIPRule."""
    entities = [
        EntityCreate(
            investigation_id="inv-1",
            entity_type=EntityType.DOMAIN,
            normalized_value="target.com",
            display_value="target.com",
            confidence=100.0,
            meta_info={"is_subdomain": False, "registered_domain": "target.com"},
        ),
        EntityCreate(
            investigation_id="inv-1",
            entity_type=EntityType.SUBDOMAIN,
            normalized_value="vpn.target.com",
            display_value="vpn.target.com",
            confidence=95.0,
            meta_info={"is_subdomain": True, "registered_domain": "target.com", "resolved_ips": ["198.51.100.1"]},
        ),
        EntityCreate(
            investigation_id="inv-1",
            entity_type=EntityType.IP,
            normalized_value="198.51.100.1",
            display_value="198.51.100.1",
            confidence=100.0,
        ),
    ]

    engine = CorrelationEngine()
    rels = engine.correlate(entities, "inv-1")
    assert len(rels) >= 2

    sub_rel = next(r for r in rels if r.relationship_type == RelationshipType.SUBDOMAIN_OF)
    assert sub_rel.source_entity_id == "vpn.target.com"
    assert sub_rel.target_entity_id == "target.com"
    assert "DNS hierarchy" in sub_rel.reason

    ip_rel = next(r for r in rels if r.relationship_type == RelationshipType.RESOLVES_TO)
    assert ip_rel.source_entity_id == "vpn.target.com"
    assert ip_rel.target_entity_id == "198.51.100.1"


def test_username_email_and_domain_correlation():
    """Test EmailDomainMatchRule and UsernameEmailCorrelationRule."""
    entities = [
        EntityCreate(
            investigation_id="inv-2",
            entity_type=EntityType.DOMAIN,
            normalized_value="security.org",
            display_value="security.org",
        ),
        EntityCreate(
            investigation_id="inv-2",
            entity_type=EntityType.EMAIL,
            normalized_value="analyst@security.org",
            display_value="analyst@security.org",
            meta_info={"domain": "security.org"},
        ),
        EntityCreate(
            investigation_id="inv-2",
            entity_type=EntityType.USERNAME,
            normalized_value="analyst",
            display_value="analyst",
        ),
    ]

    engine = CorrelationEngine()
    rels = engine.correlate(entities, "inv-2")
    assert len(rels) >= 2

    email_dom_rel = next(r for r in rels if r.relationship_type == RelationshipType.USES)
    assert email_dom_rel.source_entity_id == "analyst@security.org"
    assert email_dom_rel.target_entity_id == "security.org"

    user_email_rel = next(r for r in rels if r.relationship_type == RelationshipType.POSSIBLY_BELONGS_TO)
    assert user_email_rel.source_entity_id == "analyst"
    assert user_email_rel.target_entity_id == "analyst@security.org"
