"""Certificate Transparency crt.sh collector adapter."""

import hashlib
import json
from typing import Any, Dict, List, Optional

import httpx
from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType
from app.core.logging import logger
from app.services.target_validator import TargetValidator


class CrtshCollector(BaseCollector):
    """Adapter querying Certificate Transparency logs via crt.sh."""

    name: str = CollectorName.CRTSH
    display_name: str = "Certificate Transparency (crt.sh)"
    supported_target_types: List[TargetType] = [TargetType.DOMAIN]
    default_timeout_seconds: int = 60

    def validate_target(self, target: str) -> bool:
        """Validates target domain."""
        try:
            TargetValidator.validate(target, TargetType.DOMAIN)
            return True
        except Exception:
            return False

    async def health_check(self) -> bool:
        return True

    async def collect(self, target: str, context: Optional[Dict[str, Any]] = None) -> RawCollectorResult:
        """Queries crt.sh JSON endpoint for historical certificates."""
        if context and "mock_output" in context:
            mock_data = context["mock_output"]
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                stdout=json.dumps(mock_data),
                parsed_json=mock_data,
            )

        url = f"https://crt.sh/?q=%.{target}&output=json"
        results = []

        try:
            async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": "OSINT-X-Defensive-Assessment"}) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    results = resp.json()
        except Exception as exc:
            logger.debug("crt.sh query for %s failed: %s", target, str(exc))

        return RawCollectorResult(
            collector_name=self.name,
            target=target,
            target_type=TargetType.DOMAIN,
            stdout=json.dumps(results),
            parsed_json=results,
        )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses cert entries extracting unique names."""
        if not isinstance(raw_result.parsed_json, list):
            return []

        unique_names = set()
        items = []
        for cert in raw_result.parsed_json:
            name_value = cert.get("name_value", "")
            for name in name_value.split("\n"):
                clean_name = name.strip().lower().lstrip("*.")
                if clean_name and clean_name not in unique_names:
                    unique_names.add(clean_name)
                    items.append({
                        "name": clean_name,
                        "issuer_name": cert.get("issuer_name"),
                        "logged_at": cert.get("entry_timestamp"),
                        "not_before": cert.get("not_before"),
                        "not_after": cert.get("not_after"),
                    })
        return items

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts cert SAN into StandardizedFinding."""
        fqdn = item.get("name") or target
        fqdn_clean = fqdn.lower().strip()
        issuer = item.get("issuer_name") or "Unknown CA"

        evidence_payload = {
            "source_collector": self.name,
            "target_domain": target,
            "discovered_name": fqdn_clean,
            "issuer": issuer,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        return StandardizedFinding(
            source=self.name,
            entity_type="SUBDOMAIN" if fqdn_clean != target.lower() else "DOMAIN",
            value=fqdn_clean,
            finding_type=FindingType.CERTIFICATE_SAN,
            severity=FindingSeverity.INFO,
            title=f"Certificate SAN: {fqdn_clean}",
            description=f"Certificate Transparency record issued by '{issuer}' includes '{fqdn_clean}'.",
            metadata={"fqdn": fqdn_clean, "issuer": issuer, "target": target},
            confidence=95.0,
            evidence={
                "evidence_type": "certificate_transparency",
                "hash_digest": evidence_hash,
                "payload": evidence_payload,
            },
            provenance_url=f"https://crt.sh/?q={fqdn_clean}",
        )
