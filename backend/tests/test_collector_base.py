"""Tests for Collector abstraction, registry, and sandboxed runner."""

import sys
from typing import Any, Dict, List
import pytest

from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.collectors.registry import CollectorRegistry
from app.collectors.runner import run_subprocess_sandboxed
from app.core.constants import FindingSeverity, FindingType, TargetType
from app.core.exceptions import CollectorNotFoundError, CollectorTimeoutError


class MockEmailCollector(BaseCollector):
    """Mock collector adapter for testing base protocol."""
    name = "mock_email_collector"
    display_name = "Mock Email Collector"
    supported_target_types = [TargetType.EMAIL]

    def validate_target(self, target: str) -> bool:
        return "@" in target

    async def collect(self, target: str, context: dict = None) -> RawCollectorResult:
        return RawCollectorResult(
            collector_name=self.name,
            target=target,
            target_type=TargetType.EMAIL,
            stdout='{"service": "MockService", "account_exists": true}',
            parsed_json={"service": "MockService", "account_exists": True},
        )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        return [raw_result.parsed_json] if raw_result.parsed_json else []

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        return StandardizedFinding(
            source=self.name,
            entity_type="EMAIL",
            value=target,
            finding_type=FindingType.ACCOUNT_PRESENCE,
            severity=FindingSeverity.LOW,
            title=f"Account found on {item.get('service')}",
            metadata=item,
            confidence=90.0,
        )

    async def health_check(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_base_collector_lifecycle():
    """Test full execute lifecycle on mock collector."""
    collector = MockEmailCollector()
    findings = await collector.execute("analyst@example.com")
    assert len(findings) == 1
    f = findings[0]
    assert f.source == "mock_email_collector"
    assert f.value == "analyst@example.com"
    assert f.finding_type == FindingType.ACCOUNT_PRESENCE
    assert f.confidence == 90.0


def test_collector_registry():
    """Test registering and querying collectors."""
    reg = CollectorRegistry()
    collector = MockEmailCollector()
    reg.register(collector)

    assert reg.get("mock_email_collector") == collector
    email_collectors = reg.list_for_target_type(TargetType.EMAIL)
    assert len(email_collectors) == 1
    assert email_collectors[0].name == "mock_email_collector"

    domain_collectors = reg.list_for_target_type(TargetType.DOMAIN)
    assert len(domain_collectors) == 0

    with pytest.raises(CollectorNotFoundError):
        reg.get("non_existent_collector")


@pytest.mark.asyncio
async def test_subprocess_sandboxed_success():
    """Test successful command execution via sandboxed runner."""
    cmd = [sys.executable, "-c", "print('hello osintx')"]
    exit_code, stdout, stderr, duration = await run_subprocess_sandboxed(cmd, timeout_seconds=5)
    assert exit_code == 0
    assert "hello osintx" in stdout
    assert duration >= 0


@pytest.mark.asyncio
async def test_subprocess_sandboxed_timeout():
    """Test subprocess runner enforcing strict timeout."""
    cmd = [sys.executable, "-c", "import time; time.sleep(5)"]
    with pytest.raises(CollectorTimeoutError):
        await run_subprocess_sandboxed(cmd, timeout_seconds=1)
