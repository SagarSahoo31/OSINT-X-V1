"""OWASP Amass attack-surface discovery collector adapter."""

import hashlib
import json
import shutil
from typing import Any, Dict, List, Optional

from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.collectors.runner import run_subprocess_sandboxed
from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType
from app.core.logging import logger
from app.services.target_validator import TargetValidator


class AmassCollector(BaseCollector):
    """Adapter for OWASP Amass attack-surface and subdomain discovery."""

    name: str = CollectorName.AMASS
    display_name: str = "OWASP Amass Attack-Surface Discovery"
    supported_target_types: List[TargetType] = [TargetType.DOMAIN]
    default_timeout_seconds: int = 180

    def validate_target(self, target: str) -> bool:
        """Validates target domain format."""
        try:
            TargetValidator.validate(target, TargetType.DOMAIN)
            return True
        except Exception:
            return False

    async def health_check(self) -> bool:
        """Checks if amass binary is available."""
        return shutil.which("amass") is not None

    async def collect(self, target: str, context: Optional[Dict[str, Any]] = None) -> RawCollectorResult:
        """Executes Amass passive enumeration."""
        if context and "mock_output" in context:
            mock_data = context["mock_output"]
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                stdout=json.dumps(mock_data),
                parsed_json=mock_data,
            )

        if not shutil.which("amass"):
            logger.info("Amass binary not installed on host PATH; using fallback mode.")
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                exit_code=0,
                stdout="",
            )

        cmd = [
            "amass",
            "enum",
            "-passive",
            "-d",
            target,
            "-json",
            "out.json",
        ]

        try:
            exit_code, stdout, stderr, duration = await run_subprocess_sandboxed(
                cmd,
                timeout_seconds=self.default_timeout_seconds,
            )
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time_ms=duration,
            )
        except Exception as exc:
            logger.warning("Amass execution failed for %s: %s", target, str(exc))
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                exit_code=1,
                stderr=str(exc),
            )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses Amass JSON Lines output."""
        if raw_result.parsed_json:
            if isinstance(raw_result.parsed_json, list):
                return raw_result.parsed_json
            elif isinstance(raw_result.parsed_json, dict):
                return [raw_result.parsed_json]

        items = []
        if not raw_result.stdout:
            return items

        for line in raw_result.stdout.splitlines():
            line_clean = line.strip()
            if not line_clean:
                continue
            if line_clean.startswith("{") and line_clean.endswith("}"):
                try:
                    data = json.loads(line_clean)
                    if isinstance(data, dict):
                        items.append(data)
                except Exception:
                    pass
            elif "." in line_clean and " " not in line_clean:
                items.append({"name": line_clean, "domain": raw_result.target})

        return items

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts raw Amass record to StandardizedFinding."""
        fqdn = item.get("name") or target
        fqdn_clean = fqdn.lower().strip()
        addresses = item.get("addresses", [])
        asn = item.get("asn")
        sources = item.get("sources", ["amass"])

        resolved_ips = []
        for addr in addresses:
            if isinstance(addr, dict) and "ip" in addr:
                resolved_ips.append(addr["ip"])
            elif isinstance(addr, str):
                resolved_ips.append(addr)

        meta = {
            "fqdn": fqdn_clean,
            "resolved_ips": resolved_ips,
            "sources": sources,
            "root_domain": target.lower(),
        }
        if asn:
            meta["asn"] = asn

        evidence_payload = {
            "source_collector": self.name,
            "target_domain": target,
            "discovered_fqdn": fqdn_clean,
            "raw_attributes": item,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        return StandardizedFinding(
            source=self.name,
            entity_type="SUBDOMAIN" if fqdn_clean != target.lower() else "DOMAIN",
            value=fqdn_clean,
            finding_type=FindingType.SUBDOMAIN_DISCOVERY,
            severity=FindingSeverity.INFO,
            title=f"Subdomain Discovered: {fqdn_clean}",
            description=f"Passive DNS discovery identified active subdomain '{fqdn_clean}' for target '{target}'.",
            metadata=meta,
            confidence=95.0,
            evidence={
                "evidence_type": "dns_subdomain_discovery",
                "hash_digest": evidence_hash,
                "payload": evidence_payload,
            },
            provenance_url=f"https://{fqdn_clean}",
        )
