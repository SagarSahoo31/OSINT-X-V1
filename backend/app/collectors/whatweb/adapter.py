"""WhatWeb technology identification collector adapter."""

import hashlib
import json
import re
from typing import Any, Dict, List, Optional

import httpx
from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType
from app.core.logging import logger
from app.services.target_validator import TargetValidator


class WhatWebCollector(BaseCollector):
    """Adapter for identifying technology stack components and headers."""

    name: str = CollectorName.WHATWEB
    display_name: str = "WhatWeb Technology Detection"
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
        """Fingerprints technologies via HTTP headers, cookies, and body patterns."""
        if context and "mock_output" in context:
            mock_data = context["mock_output"]
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.DOMAIN,
                stdout=json.dumps(mock_data),
                parsed_json=mock_data,
            )

        url = target if target.startswith(("http://", "https://")) else f"https://{target}"
        detected: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(verify=False, timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url)
                headers = resp.headers
                body = resp.text

                # 1. Server header
                if "server" in headers:
                    detected.append({"name": headers["server"], "category": "web_server", "confidence": 100})
                # 2. X-Powered-By
                if "x-powered-by" in headers:
                    detected.append({"name": headers["x-powered-by"], "category": "framework", "confidence": 100})
                # 3. Cloudflare
                if "cf-ray" in headers or "cloudflare" in headers.get("server", "").lower():
                    detected.append({"name": "Cloudflare", "category": "cdn_waf", "confidence": 100})
                # 4. WordPress
                if "/wp-content/" in body or "/wp-includes/" in body:
                    detected.append({"name": "WordPress", "category": "cms", "confidence": 95})
                # 5. React
                if "react" in body.lower() or "_next" in body:
                    detected.append({"name": "React / Next.js", "category": "frontend_framework", "confidence": 90})
        except Exception as exc:
            logger.debug("Technology probe failed for %s: %s", url, str(exc))

        return RawCollectorResult(
            collector_name=self.name,
            target=target,
            target_type=TargetType.DOMAIN,
            stdout=json.dumps(detected),
            parsed_json=detected,
        )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses detected technologies."""
        if isinstance(raw_result.parsed_json, list):
            return raw_result.parsed_json
        return []

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts detected technology into StandardizedFinding."""
        tech_name = item.get("name") or "Unknown Tech"
        category = item.get("category", "general")
        confidence = float(item.get("confidence", 90.0))

        evidence_payload = {
            "source_collector": self.name,
            "target": target,
            "technology": tech_name,
            "category": category,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        return StandardizedFinding(
            source=self.name,
            entity_type="TECHNOLOGY",
            value=tech_name,
            finding_type=FindingType.TECHNOLOGY_STACK,
            severity=FindingSeverity.INFO,
            title=f"Technology Stack: {tech_name}",
            description=f"Identified {category} technology '{tech_name}' running on '{target}'.",
            metadata={"technology": tech_name, "category": category, "target": target},
            confidence=confidence,
            evidence={
                "evidence_type": "technology_fingerprint",
                "hash_digest": evidence_hash,
                "payload": evidence_payload,
            },
        )
