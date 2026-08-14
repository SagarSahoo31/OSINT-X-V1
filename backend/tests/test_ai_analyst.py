"""Tests for Ollama AI Analyst and PromptBuilder."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ollama_client import ollama_analyst
from app.ai.prompts import PromptBuilder
from app.core.constants import TargetType
from app.models.investigation import Investigation


def test_prompt_builder():
    """Verify prompt builder formats evidence and instructions correctly."""
    prompt = PromptBuilder.build_investigation_analysis_prompt(
        target="target.org",
        target_type="DOMAIN",
        entities=[{"type": "DOMAIN", "value": "target.org"}],
        relationships=[],
        findings=[],
        risk_score=45.0,
    )
    assert "target.org" in prompt
    assert "45.0" in prompt
    assert "Defensive Remediation" in prompt


@pytest.mark.asyncio
async def test_ollama_fallback_analysis():
    """Verify fallback deterministic analysis when Ollama is offline."""
    res = await ollama_analyst.analyze_investigation(
        target="target.org",
        target_type="DOMAIN",
        entities=[{"entity_type": "DOMAIN", "normalized_value": "target.org"}],
        relationships=[],
        findings=[],
        risk_score=35.0,
    )
    assert "analysis" in res
    assert "[OBSERVED EVIDENCE]" in res["analysis"]
    assert "[DEFENSIVE REMEDIATION]" in res["analysis"]


@pytest.mark.asyncio
async def test_ai_api_endpoint(async_client: AsyncClient, async_db_session: AsyncSession):
    """Test POST /api/v1/investigations/{id}/ai/analyze."""
    inv = Investigation(
        title="AI Analysis Test",
        target_input="target.org",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
    )
    async_db_session.add(inv)
    await async_db_session.commit()

    res = await async_client.post(f"/api/v1/investigations/{inv.id}/ai/analyze")
    assert res.status_code == 200
    data = res.json()
    assert data["investigation_id"] == inv.id
    assert "analysis" in data
