"""Unit tests for Holehe email discovery collector adapter."""

import pytest
from app.collectors.holehe.adapter import HoleheCollector
from app.core.constants import FindingSeverity, FindingType


@pytest.mark.asyncio
async def test_holehe_adapter_validation():
    """Test target validation rules for Holehe."""
    collector = HoleheCollector()
    assert collector.validate_target("analyst@example.com") is True
    assert collector.validate_target("not-an-email") is False


@pytest.mark.asyncio
async def test_holehe_adapter_mock_execution():
    """Test full execution, parsing, and normalization from structured mock data."""
    collector = HoleheCollector()
    mock_data = [
        {"name": "GitHub", "domain": "github.com", "exists": True, "emailrecovery": "a*****t@g****.com"},
        {"name": "Spotify", "domain": "spotify.com", "exists": True, "rateLimit": False},
        {"name": "Twitter", "domain": "twitter.com", "exists": False},
    ]

    findings = await collector.execute("analyst@example.com", context={"mock_output": mock_data})
    # Should only return the 2 accounts where exists == True
    assert len(findings) == 2

    github_finding = next(f for f in findings if f.metadata["service_name"] == "GitHub")
    assert github_finding.source == "holehe"
    assert github_finding.value == "analyst@example.com"
    assert github_finding.finding_type == FindingType.ACCOUNT_PRESENCE
    assert github_finding.confidence == 90.0
    assert github_finding.metadata["email_recovery_hint"] == "a*****t@g****.com"
    assert "evidence" in github_finding.model_dump()
    assert github_finding.evidence["hash_digest"] is not None


@pytest.mark.asyncio
async def test_holehe_text_output_parsing():
    """Test parsing text CLI output format."""
    collector = HoleheCollector()
    raw_stdout = """
    [+] github.com
    [-] twitter.com
    [+] spotify.com
    """
    raw_res = collector.parse(collector.collect.__annotations__ and type("MockResult", (), {"stdout": raw_stdout, "parsed_json": None})())
    assert len(raw_res) == 2
    assert raw_res[0]["name"] == "github.com"
