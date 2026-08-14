"""Unit tests for OWASP Amass attack-surface discovery adapter."""

import pytest
from app.collectors.amass.adapter import AmassCollector
from app.core.constants import FindingType


@pytest.mark.asyncio
async def test_amass_adapter_validation():
    """Test domain target validation."""
    collector = AmassCollector()
    assert collector.validate_target("example.com") is True
    assert collector.validate_target("sub.target.co.uk") is True
    assert collector.validate_target("not-a-domain") is False


@pytest.mark.asyncio
async def test_amass_adapter_mock_execution():
    """Test full execution and normalization on mock JSON Lines data."""
    collector = AmassCollector()
    mock_data = [
        {
            "name": "vpn.target.org",
            "domain": "target.org",
            "addresses": [{"ip": "198.51.100.25", "cidr": "198.51.100.0/24", "asn": 13335}],
            "sources": ["Crtsh", "DNSDumpster"],
        },
        {
            "name": "api.target.org",
            "domain": "target.org",
            "addresses": [{"ip": "198.51.100.26"}],
            "sources": ["AlienVault"],
        },
    ]

    findings = await collector.execute("target.org", context={"mock_output": mock_data})
    assert len(findings) == 2

    vpn_finding = next(f for f in findings if f.value == "vpn.target.org")
    assert vpn_finding.source == "amass"
    assert vpn_finding.entity_type == "SUBDOMAIN"
    assert vpn_finding.finding_type == FindingType.SUBDOMAIN_DISCOVERY
    assert vpn_finding.confidence == 95.0
    assert "198.51.100.25" in vpn_finding.metadata["resolved_ips"]
    assert vpn_finding.evidence["hash_digest"] is not None
