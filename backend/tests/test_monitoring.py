"""Tests for Monitoring and scan delta comparison service."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EntityType, FindingSeverity, FindingType, TargetType
from app.models.entity import Entity
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.models.risk import RiskScore
from app.services.monitoring_service import MonitoringService


@pytest.mark.asyncio
async def test_monitoring_scan_comparison(async_db_session: AsyncSession):
    """Test comparing two scans to detect added and removed assets."""
    # 1. Baseline Scan
    inv1 = Investigation(title="Scan 1 (Baseline)", target_input="target.org", target_type=TargetType.DOMAIN, is_authorized=True)
    async_db_session.add(inv1)
    await async_db_session.flush()

    e1_base = Entity(investigation_id=inv1.id, entity_type=EntityType.DOMAIN, normalized_value="target.org", display_value="target.org")
    e2_base = Entity(investigation_id=inv1.id, entity_type=EntityType.SUBDOMAIN, normalized_value="old-vpn.target.org", display_value="old-vpn.target.org")
    risk1 = RiskScore(investigation_id=inv1.id, overall_score=30.0, severity_score=20.0, exposure_score=40.0, confidence_weight=1.0)
    async_db_session.add_all([e1_base, e2_base, risk1])

    # 2. Current Scan (old-vpn removed, new-api added)
    inv2 = Investigation(title="Scan 2 (Current)", target_input="target.org", target_type=TargetType.DOMAIN, is_authorized=True)
    async_db_session.add(inv2)
    await async_db_session.flush()

    e1_curr = Entity(investigation_id=inv2.id, entity_type=EntityType.DOMAIN, normalized_value="target.org", display_value="target.org")
    e3_curr = Entity(investigation_id=inv2.id, entity_type=EntityType.SUBDOMAIN, normalized_value="new-api.target.org", display_value="new-api.target.org")
    risk2 = RiskScore(investigation_id=inv2.id, overall_score=50.0, severity_score=40.0, exposure_score=60.0, confidence_weight=1.0)
    async_db_session.add_all([e1_curr, e3_curr, risk2])
    await async_db_session.commit()

    comparison = await MonitoringService.compare_scans(async_db_session, inv1.id, inv2.id)
    assert comparison["risk_assessment"]["risk_delta"] == 20.0
    assert comparison["risk_assessment"]["trend"] == "INCREASED"
    assert comparison["asset_changes"]["new_assets_count"] == 1
    assert comparison["asset_changes"]["removed_assets_count"] == 1
    assert comparison["asset_changes"]["persistent_assets_count"] == 1
    assert comparison["asset_changes"]["new_assets"][0]["value"] == "new-api.target.org"
    assert comparison["asset_changes"]["removed_assets"][0]["value"] == "old-vpn.target.org"


@pytest.mark.asyncio
async def test_timeline_endpoint(async_client: AsyncClient, async_db_session: AsyncSession):
    """Test GET /api/v1/investigations/{id}/timeline."""
    inv = Investigation(title="Timeline Test", target_input="target.org", target_type=TargetType.DOMAIN, is_authorized=True)
    async_db_session.add(inv)
    await async_db_session.flush()

    f = Finding(
        investigation_id=inv.id,
        source_tool="dns",
        finding_type=FindingType.DNS_RECORD,
        title="Discovered A Record",
    )
    async_db_session.add(f)
    await async_db_session.commit()

    res = await async_client.get(f"/api/v1/investigations/{inv.id}/timeline")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 2
    assert events[0]["event_type"] == "INVESTIGATION_CREATED"
    assert events[1]["event_type"] == "FINDING_DISCOVERED"
