"""Unified collector protocol, finding abstractions, and base class."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType


class RawCollectorResult(BaseModel):
    """Raw output payload produced directly by an OSINT collector adapter."""
    collector_name: str
    target: str
    target_type: TargetType
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    parsed_json: Optional[Any] = None
    execution_time_ms: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StandardizedFinding(BaseModel):
    """Canonical finding structure returned by all OSINT-X collectors."""
    source: str
    entity_type: str
    value: str
    finding_type: FindingType
    severity: FindingSeverity = FindingSeverity.INFO
    title: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=80.0, ge=0.0, le=100.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: Dict[str, Any] = Field(default_factory=dict)
    provenance_url: Optional[str] = None


class BaseCollector(ABC):
    """Abstract base class establishing the contract for all OSINT tool adapters."""

    name: str = "base_collector"
    display_name: str = "Base Collector"
    supported_target_types: List[TargetType] = []
    default_timeout_seconds: int = 180

    @abstractmethod
    def validate_target(self, target: str) -> bool:
        """Validates if the target is applicable and safe for this specific collector."""
        pass

    @abstractmethod
    async def collect(self, target: str, context: Optional[Dict[str, Any]] = None) -> RawCollectorResult:
        """Executes the OSINT tool or API client in sandbox mode and captures raw output."""
        pass

    @abstractmethod
    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses heterogeneous tool output into intermediate structured dictionaries."""
        pass

    @abstractmethod
    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts an intermediate parsed item into the canonical OSINT-X StandardizedFinding."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifies if the collector executable or underlying service is installed and operational."""
        pass

    async def execute(self, target: str, context: Optional[Dict[str, Any]] = None) -> List[StandardizedFinding]:
        """
        Complete execution template: validate -> collect -> parse -> normalize.
        Guarantees standardized findings and preserves provenance.
        """
        if not self.validate_target(target):
            return []

        raw_result = await self.collect(target, context=context)
        parsed_items = self.parse(raw_result)

        findings: List[StandardizedFinding] = []
        for item in parsed_items:
            try:
                finding = self.normalize_item(item, target)
                findings.append(finding)
            except Exception as exc:
                # Discard malformed item but do not break entire collection run
                continue

        return findings
