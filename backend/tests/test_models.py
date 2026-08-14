"""Tests for SQLAlchemy database models, relationships, and cascade operations."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from app.core.constants import (
    CollectorJobStatus,
    CollectorName,
    EntityType,
    FindingSeverity,
    FindingType,
    InvestigationStatus,
    RelationshipType,
    TargetType,
    UserRole,
)
from app.models.user import User, AuditLog
from app.models.investigation import Investigation, CollectorJob
from app.models.entity import Entity, Relationship
from app.models.finding import Finding, Evidence
from app.models.risk import RiskScore
from app.models.report import Report


def test_create_user_and_audit_log(db_session: Session):
    """Test user creation and associated audit log creation."""
    user = User(
        email="analyst@osintx.org",
        username="analyst1",
        hashed_password="hashed_secure_password",
        role=UserRole.ANALYST,
        full_name="OSINT Analyst",
    )
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert user.role == UserRole.ANALYST
    assert user.created_at is not None

    log = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        ip_address="127.0.0.1",
        details={"method": "password"},
    )
    db_session.add(log)
    db_session.flush()

    assert log.id is not None
    assert log.user.username == "analyst1"


def test_create_investigation_and_collector_job(db_session: Session):
    """Test investigation lifecycle creation and collector job tracking."""
    user = User(
        email="lead@osintx.org",
        username="lead_investigator",
        hashed_password="hashed_secure_password",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.flush()

    inv = Investigation(
        title="Target Domain Footprint",
        description="Defensive attack-surface assessment",
        target_input="example.com",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
        authorization_notes="Authorized by domain owner for penetration test",
        status=InvestigationStatus.QUEUED,
        user_id=user.id,
    )
    db_session.add(inv)
    db_session.flush()

    assert inv.id is not None
    assert inv.status == InvestigationStatus.QUEUED
    assert inv.is_authorized is True

    job = CollectorJob(
        investigation_id=inv.id,
        collector_name=CollectorName.AMASS,
        status=CollectorJobStatus.RUNNING,
    )
    db_session.add(job)
    db_session.flush()

    assert job.id is not None
    assert job.investigation.title == "Target Domain Footprint"
    assert len(inv.collector_jobs) == 1


def test_entities_and_relationships(db_session: Session):
    """Test entity resolution and directed relationship creation."""
    inv = Investigation(
        title="Identity Mapping",
        target_input="target_user",
        target_type=TargetType.USERNAME,
        is_authorized=True,
    )
    db_session.add(inv)
    db_session.flush()

    e1 = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.USERNAME,
        normalized_value="target_user",
        display_value="target_user",
        confidence=100.0,
        source_provenance=[{"tool": "maigret", "source": "github"}],
    )
    e2 = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.EMAIL,
        normalized_value="target_user@example.com",
        display_value="target_user@example.com",
        confidence=90.0,
        source_provenance=[{"tool": "holehe", "source": "google"}],
    )
    db_session.add_all([e1, e2])
    db_session.flush()

    rel = Relationship(
        investigation_id=inv.id,
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type=RelationshipType.ASSOCIATED_WITH,
        confidence=85.0,
        reason="Matching email and username across independent profiles",
        source_tool="correlation_engine",
        evidence={"matched_fields": ["username_prefix"]},
    )
    db_session.add(rel)
    db_session.flush()

    assert len(e1.outgoing_relationships) == 1
    assert len(e2.incoming_relationships) == 1
    assert rel.relationship_type == RelationshipType.ASSOCIATED_WITH


def test_findings_and_evidence(db_session: Session):
    """Test finding recording with supporting evidence snapshots."""
    inv = Investigation(
        title="Exposure Scan",
        target_input="admin@example.com",
        target_type=TargetType.EMAIL,
        is_authorized=True,
    )
    db_session.add(inv)
    db_session.flush()

    finding = Finding(
        investigation_id=inv.id,
        source_tool="holehe",
        finding_type=FindingType.ACCOUNT_PRESENCE,
        severity=FindingSeverity.LOW,
        title="Account Registered on GitHub",
        description="Email address is associated with an active GitHub account",
        raw_data={"rate_limit": False, "exists": True},
        normalized_data={"site": "GitHub", "category": "development"},
        confidence=95.0,
    )
    db_session.add(finding)
    db_session.flush()

    evidence = Evidence(
        finding_id=finding.id,
        evidence_type="http_response",
        content={"status_code": 200, "body_snippet": "Account exists"},
        provenance_url="https://api.github.com",
    )
    db_session.add(evidence)
    db_session.flush()

    assert len(finding.evidence_items) == 1
    assert finding.evidence_items[0].provenance_url == "https://api.github.com"


def test_cascade_delete_investigation(db_session: Session):
    """Verify deleting an investigation cascades cleanly to child entities and findings."""
    inv = Investigation(
        title="Temporary Assessment",
        target_input="test.org",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
    )
    db_session.add(inv)
    db_session.flush()

    job = CollectorJob(
        investigation_id=inv.id,
        collector_name=CollectorName.DNS,
        status=CollectorJobStatus.COMPLETED,
    )
    e = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.DOMAIN,
        normalized_value="test.org",
        display_value="test.org",
    )
    f = Finding(
        investigation_id=inv.id,
        source_tool="dns",
        finding_type=FindingType.DNS_RECORD,
        title="A Record",
    )
    risk = RiskScore(
        investigation_id=inv.id,
        overall_score=45.0,
        severity_score=30.0,
        exposure_score=60.0,
        confidence_weight=0.9,
        explanation=["Public DNS record present"],
    )
    report = Report(
        investigation_id=inv.id,
        format="JSON",
        title="Assessment Report",
        file_path="/tmp/test.json",
    )
    db_session.add_all([job, e, f, risk, report])
    db_session.flush()

    inv_id = inv.id
    db_session.delete(inv)
    db_session.flush()

    assert db_session.query(CollectorJob).filter_by(investigation_id=inv_id).count() == 0
    assert db_session.query(Entity).filter_by(investigation_id=inv_id).count() == 0
    assert db_session.query(Finding).filter_by(investigation_id=inv_id).count() == 0
    assert db_session.query(RiskScore).filter_by(investigation_id=inv_id).count() == 0
    assert db_session.query(Report).filter_by(investigation_id=inv_id).count() == 0
