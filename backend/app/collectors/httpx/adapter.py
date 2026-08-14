"""HTTPX web endpoint probing collector adapter."""

import hashlib
import json
import re
from typing import Any, Dict, List, Optional

import httpx
from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType
from app.core.logging import logger
from app.services.target_validator import TargetValidator


class HTTPXCollector(BaseCollector):
    """Adapter for HTTP/HTTPS web probing and title/header discovery."""

    name: str = CollectorName.HTTPX
    display_name: str = "HTTPX Web Prober"
    supported_target_types: List[TargetType] = [TargetType.DOMAIN, TargetType.IP, TargetType.URL]
    default_timeout_seconds: int = 45

    def validate_target(self, target: str) -> bool:
        """Validates target format."""
        for ttype in (TargetType.DOMAIN, TargetType.IP, TargetType.URL):
            try:
                TargetValidator.validate(target, ttype)
                return True
            except Exception:
                continue
        return False

    async def health_check(self) -> bool:
        return True

    async def collect(self, target: str, context: Optional[Dict[str, Any]] = None) -> RawCollectorResult:
        """Probes HTTP and HTTPS endpoints for target host."""
        if context and "mock_output" in context:
            mock_data = context["mock_output"]
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                stdout=json.dumps(mock_data),
                parsed_json=mock_data,
            )

        urls_to_probe = []
        if target.startswith(("http://", "https://")):
            urls_to_probe.append(target)
        else:
            urls_to_probe = [f"https://{target}", f"http://{target}"]

        results = []
        async with httpx.AsyncClient(verify=False, timeout=10.0, follow_redirects=True) as client:
            for url in urls_to_probe:
                try:
                    resp = await client.get(url)
                    title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else ""
                    server = resp.headers.get("server", "")

                    results.append({
                        "url": str(resp.url),
                        "status_code": resp.status_code,
                        "title": title,
                        "server": server,
                        "content_length": len(resp.content),
                        "headers": dict(resp.headers),
                    })
                except Exception as exc:
                    logger.debug("HTTPX probe failed for %s: %s", url, str(exc))

        return RawCollectorResult(
            collector_name=self.name,
            target=target,
            target_type=TargetType.DOMAIN,
            stdout=json.dumps(results),
            parsed_json=results,
        )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses probe results into endpoint items."""
        if isinstance(raw_result.parsed_json, list):
            return raw_result.parsed_json
        return []

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts probed endpoint into StandardizedFinding."""
        url = item.get("url", f"https://{target}")
        status_code = item.get("status_code", 200)
        title = item.get("title") or "No HTML Title"
        server = item.get("server") or "Unknown"

        severity = FindingSeverity.INFO
        if status_code in (500, 502, 503):
            severity = FindingSeverity.LOW
        elif "admin" in url.lower() or "login" in url.lower():
            severity = FindingSeverity.MEDIUM

        evidence_payload = {
            "source_collector": self.name,
            "url": url,
            "status_code": status_code,
            "server": server,
            "title": title,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        return StandardizedFinding(
            source=self.name,
            entity_type="URL",
            value=url,
            finding_type=FindingType.HTTP_ENDPOINT,
            severity=severity,
            title=f"Web Service [{status_code}]: {url}",
            description=f"HTTP endpoint responds with status {status_code}. Title: '{title}'. Server: '{server}'.",
            metadata={
                "url": url,
                "status_code": status_code,
                "title": title,
                "server": server,
                "headers": item.get("headers", {}),
            },
            confidence=100.0,
            evidence={
                "evidence_type": "http_probe",
                "hash_digest": evidence_hash,
                "payload": evidence_payload,
            },
            provenance_url=url,
        )
