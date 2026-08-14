"""Unit tests for Maigret username footprint discovery adapter."""

import pytest
from app.collectors.maigret.adapter import MaigretCollector
from app.core.constants import FindingType


@pytest.mark.asyncio
async def test_maigret_adapter_validation():
    """Test target validation for usernames in Maigret."""
    collector = MaigretCollector()
    assert collector.validate_target("security_analyst") is True
    assert collector.validate_target("a") is False
    assert collector.validate_target("bad username with space") is False


@pytest.mark.asyncio
async def test_maigret_mock_execution():
    """Test full execution and normalization from structured mock dictionary."""
    collector = MaigretCollector()
    mock_dict = {
        "GitHub": {
            "url_user": "https://github.com/security_analyst",
            "status": "Found",
            "category": "coding",
            "tags": ["developer", "vcs"],
        },
        "Reddit": {
            "url_user": "https://reddit.com/user/security_analyst",
            "status": "Claimed",
            "category": "forum",
        },
    }

    findings = await collector.execute("security_analyst", context={"mock_output": mock_dict})
    assert len(findings) == 2

    github_finding = next(f for f in findings if f.metadata["site_name"] == "GitHub")
    assert github_finding.source == "maigret"
    assert github_finding.value == "security_analyst"
    assert github_finding.finding_type == FindingType.ACCOUNT_PRESENCE
    assert github_finding.metadata["profile_url"] == "https://github.com/security_analyst"
    assert github_finding.metadata["category"] == "coding"
    assert "vcs" in github_finding.metadata["tags"]
    assert github_finding.evidence["hash_digest"] is not None


@pytest.mark.asyncio
async def test_maigret_line_parsing():
    """Test line format parsing."""
    collector = MaigretCollector()
    raw_stdout = """
    [+] GitHub: https://github.com/user1
    [+] GitLab: https://gitlab.com/user1
    """
    raw_res = collector.parse(type("MockResult", (), {"stdout": raw_stdout, "parsed_json": None})())
    assert len(raw_res) == 2
    assert raw_res[0]["site_name"] == "GitHub"
    assert raw_res[0]["profile_url"] == "https://github.com/user1"
