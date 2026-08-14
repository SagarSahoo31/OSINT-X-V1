"""Tests for Report generation and download APIs."""

import os
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EntityType, FindingSeverity, FindingType, TargetType
from app.models.entity import Entity
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.models.risk import RiskScore
from app.reporting.generator import ReportGenerator


@pytest.mark.asyncio
async def test_report_generation_all_formats(async_client: AsyncClient, async_db_session: AsyncSession):
    """Test generating PDF, JSON, and CSV reports and verifying file contents."""
    inv = Investigation(
        title="Comprehensive Assessment",
        target_input="target.org",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
    )
    async_db_session.add(inv)
    await async_db_session.flush()

    e = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.DOMAIN,
        normalized_value="target.org",
        display_value="target.org",
        confidence=100.0,
    )
    f = Finding(
        investigation_id=inv.id,
        source_tool="amass",
        finding_type=FindingType.SUBDOMAIN_DISCOVERY,
        severity=FindingSeverity.LOW,
        title="Discovered Subdomain",
        confidence=95.0,
    )
    risk = RiskScore(
        investigation_id=inv.id,
        overall_score=55.0,
        severity_score=40.0,
        exposure_score=70.0,
        confidence_weight=0.95,
        explanation=["Publicly accessible domain asset."],
    )
    async_db_session.add_all([e, f, risk])
    await async_db_session.commit()

    # 1. JSON report
    res_json = await async_client.post("/api/v1/reports", json={"investigation_id": inv.id, "format": "JSON"})
    assert res_json.status_code == 201
    assert res_json.json()["format"] == "JSON"
    assert os.path.exists(res_json.json()["file_path"])

    # 2. CSV report
    res_csv = await async_client.post("/api/v1/reports", json={"investigation_id": inv.id, "format": "CSV"})
    assert res_csv.status_code == 201
    assert res_csv.json()["format"] == "CSV"
    assert os.path.exists(res_csv.json()["file_path"])

    # 3. PDF report
    res_pdf = await async_client.post("/api/v1/reports", json={"investigation_id": inv.id, "format": "PDF"})
    assert res_pdf.status_code == 201
    assert res_pdf.json()["format"] == "PDF"
    assert os.path.exists(res_pdf.json()["file_path"])

    # 4. Download PDF
    report_id = res_pdf.json()["id"]
    dl_res = await async_client.get(f"/api/v1/reports/{report_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000
