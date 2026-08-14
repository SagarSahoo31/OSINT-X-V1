"""DNS records resolution collector adapter."""

import hashlib
import json
from typing import Any, Dict, List, Optional

import dns.resolver
from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType
from app.core.logging import logger
from app.services.target_validator import TargetValidator


class DNSCollector(BaseCollector):
    """Adapter for querying DNS records (A, AAAA, CNAME, MX, TXT, NS)."""

    name: str = CollectorName.DNS
    display_name: str = "DNS Intelligence"
    supported_target_types: List[TargetType] = [TargetType.DOMAIN, TargetType.IP]
    default_timeout_seconds: int = 30

    def validate_target(self, target: str) -> bool:
        """Validates target domain or IP."""
        try:
            TargetValidator.validate(target, TargetType.DOMAIN)
            return True
        except Exception:
            try:
                TargetValidator.validate(target, TargetType.IP)
                return True
            except Exception:
                return False

    async def health_check(self) -> bool:
        return True

    async def collect(self, target: str, context: Optional[Dict[str, Any]] = None) -> RawCollectorResult:
        """Queries DNS records for domain."""
        if context and "mock_output" in context:
            mock_data = context["mock_output"]
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                stdout=json.dumps(mock_data),
                parsed_json=mock_data,
            )

        results: Dict[str, List[str]] = {}
        record_types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA"]

        resolver = dns.resolver.Resolver()
        resolver.timeout = 5.0
        resolver.lifetime = 5.0

        for rtype in record_types:
            try:
                answers = resolver.resolve(target, rtype)
                results[rtype] = [str(r.to_text()).strip('"') for r in answers]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
                results[rtype] = []
            except Exception as exc:
                logger.debug("DNS lookup for %s %s failed: %s", target, rtype, str(exc))
                results[rtype] = []

        return RawCollectorResult(
            collector_name=self.name,
            target=target,
            target_type=TargetType.DOMAIN,
            stdout=json.dumps(results),
            parsed_json=results,
        )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses DNS query results into individual record items."""
        if not raw_result.parsed_json or not isinstance(raw_result.parsed_json, dict):
            return []

        items = []
        for rtype, records in raw_result.parsed_json.items():
            for record in records:
                items.append({"record_type": rtype, "value": record, "domain": raw_result.target})
        return items

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts DNS record item to StandardizedFinding."""
        rtype = item.get("record_type", "A")
        val = item.get("value", "")

        entity_type = "IP" if rtype in ("A", "AAAA") else "DOMAIN"
        severity = FindingSeverity.INFO
        if rtype == "TXT" and any(k in val.lower() for k in ["v=spf1", "verification", "dmarc"]):
            severity = FindingSeverity.LOW

        evidence_payload = {
            "source_collector": self.name,
            "domain": target,
            "record_type": rtype,
            "record_value": val,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        return StandardizedFinding(
            source=self.name,
            entity_type=entity_type,
            value=val,
            finding_type=FindingType.DNS_RECORD,
            severity=severity,
            title=f"DNS {rtype} Record: {val}",
            description=f"DNS query for '{target}' returned {rtype} record pointing to '{val}'.",
            metadata={"record_type": rtype, "domain": target, "value": val},
            confidence=100.0,
            evidence={
                "evidence_type": "dns_record",
                "hash_digest": evidence_hash,
                "payload": evidence_payload,
            },
        )
