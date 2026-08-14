"""Tests for DNS, HTTPX, WhatWeb, and crt.sh infrastructure adapters."""

import pytest
from app.collectors import (
    CrtshCollector,
    DNSCollector,
    HTTPXCollector,
    WhatWebCollector,
    registry,
)
from app.core.constants import FindingType, TargetType


def test_all_collectors_registered():
    """Verify all 7 core collectors are registered in the catalog."""
    all_collectors = registry.list_all()
    assert len(all_collectors) >= 7
    names = {c.name for c in all_collectors}
    assert "holehe" in names
    assert "maigret" in names
    assert "amass" in names
    assert "dns" in names
    assert "httpx" in names
    assert "whatweb" in names
    assert "crtsh" in names


@pytest.mark.asyncio
async def test_dns_collector_mock():
    """Test DNS collector with mock record data."""
    collector = DNSCollector()
    mock_data = {
        "A": ["198.51.100.10"],
        "MX": ["10 mail.target.org"],
        "TXT": ["v=spf1 include:_spf.google.com ~all"],
    }
    findings = await collector.execute("target.org", context={"mock_output": mock_data})
    assert len(findings) == 3
    a_rec = next(f for f in findings if f.metadata["record_type"] == "A")
    assert a_rec.value == "198.51.100.10"
    assert a_rec.entity_type == "IP"


@pytest.mark.asyncio
async def test_httpx_collector_mock():
    """Test HTTPX collector with mock web response."""
    collector = HTTPXCollector()
    mock_data = [
        {
            "url": "https://target.org",
            "status_code": 200,
            "title": "Corporate Portal",
            "server": "nginx/1.24",
            "headers": {"server": "nginx/1.24"},
        }
    ]
    findings = await collector.execute("target.org", context={"mock_output": mock_data})
    assert len(findings) == 1
    f = findings[0]
    assert f.value == "https://target.org"
    assert f.finding_type == FindingType.HTTP_ENDPOINT
    assert f.metadata["status_code"] == 200


@pytest.mark.asyncio
async def test_whatweb_collector_mock():
    """Test WhatWeb collector with mock technology stack."""
    collector = WhatWebCollector()
    mock_data = [
        {"name": "nginx", "category": "web_server", "confidence": 100},
        {"name": "React", "category": "frontend_framework", "confidence": 90},
    ]
    findings = await collector.execute("target.org", context={"mock_output": mock_data})
    assert len(findings) == 2
    assert findings[0].entity_type == "TECHNOLOGY"
    assert findings[0].finding_type == FindingType.TECHNOLOGY_STACK


@pytest.mark.asyncio
async def test_crtsh_collector_mock():
    """Test crt.sh collector with mock Certificate Transparency logs."""
    collector = CrtshCollector()
    mock_data = [
        {"name_value": "target.org\n*.target.org\napi.target.org", "issuer_name": "Let's Encrypt"}
    ]
    findings = await collector.execute("target.org", context={"mock_output": mock_data})
    assert len(findings) == 2  # target.org and api.target.org (*.target.org is stripped)
    api_finding = next(f for f in findings if f.value == "api.target.org")
    assert api_finding.finding_type == FindingType.CERTIFICATE_SAN
    assert api_finding.metadata["issuer"] == "Let's Encrypt"
