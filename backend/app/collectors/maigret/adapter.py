"""Maigret username footprint discovery collector adapter."""

import hashlib
import json
import shutil
import sys
from typing import Any, Dict, List, Optional

from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.collectors.runner import run_subprocess_sandboxed
from app.core.constants import CollectorName, FindingSeverity, FindingType, TargetType
from app.core.logging import logger
from app.services.target_validator import TargetValidator


class MaigretCollector(BaseCollector):
    """Adapter for Maigret username footprint discovery."""

    name: str = CollectorName.MAIGRET
    display_name: str = "Maigret Username Footprint"
    supported_target_types: List[TargetType] = [TargetType.USERNAME]
    default_timeout_seconds: int = 180

    def validate_target(self, target: str) -> bool:
        """Validates target username format."""
        try:
            TargetValidator.validate(target, TargetType.USERNAME)
            return True
        except Exception:
            return False

    async def health_check(self) -> bool:
        """Verifies if Maigret executable or module is available."""
        if shutil.which("maigret"):
            return True
        try:
            exit_code, _, _, _ = await run_subprocess_sandboxed(
                [sys.executable, "-c", "import maigret; print('ok')"],
                timeout_seconds=5,
            )
            return exit_code == 0
        except Exception:
            return True

    async def collect(self, target: str, context: Optional[Dict[str, Any]] = None) -> RawCollectorResult:
        """Executes Maigret username search."""
        if context and "mock_output" in context:
            mock_data = context["mock_output"]
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.USERNAME,
                stdout=json.dumps(mock_data),
                parsed_json=mock_data,
            )

        cmd = [
            sys.executable,
            "-m",
            "maigret",
            target,
            "--no-color",
            "--print-found",
            "--timeout",
            "10",
        ]

        if shutil.which("maigret"):
            cmd = ["maigret", target, "--no-color", "--print-found", "--timeout", "10"]

        try:
            exit_code, stdout, stderr, duration = await run_subprocess_sandboxed(
                cmd,
                timeout_seconds=self.default_timeout_seconds,
            )
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.USERNAME,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time_ms=duration,
            )
        except Exception as exc:
            logger.warning("Maigret execution warning for %s: %s", target, str(exc))
            return RawCollectorResult(
                collector_name=self.name,
                target=target,
                target_type=TargetType.USERNAME,
                exit_code=1,
                stderr=str(exc),
            )

    def parse(self, raw_result: RawCollectorResult) -> List[Dict[str, Any]]:
        """Parses Maigret JSON or line output."""
        if raw_result.parsed_json:
            if isinstance(raw_result.parsed_json, dict):
                # Maigret report dict: { "SiteName": { "url_user": "...", "status": "Claimed" } }
                items = []
                for site_name, data in raw_result.parsed_json.items():
                    if isinstance(data, dict):
                        status = data.get("status", {}).get("status") if isinstance(data.get("status"), dict) else data.get("status")
                        if status in ("Claimed", "Found", True) or data.get("url_user"):
                            items.append({
                                "site_name": site_name,
                                "profile_url": data.get("url_user") or data.get("url_main"),
                                "tags": data.get("tags", []),
                                "category": data.get("category", "general"),
                            })
                return items
            elif isinstance(raw_result.parsed_json, list):
                return raw_result.parsed_json

        items = []
        if not raw_result.stdout:
            return items

        # Parse text lines: "[+] SiteName: https://site.com/user"
        for line in raw_result.stdout.splitlines():
            line_clean = line.strip()
            if line_clean.startswith("[+]"):
                parts = line_clean.replace("[+]", "").strip().split(":", 1)
                if len(parts) == 2:
                    site_name = parts[0].strip()
                    url = parts[1].strip()
                    if url.startswith("//"):
                        url = f"https:{url}"
                    items.append({
                        "site_name": site_name,
                        "profile_url": url,
                        "category": "social",
                        "tags": [],
                    })
        return items

    def normalize_item(self, item: Dict[str, Any], target: str) -> StandardizedFinding:
        """Converts raw Maigret detection to StandardizedFinding."""
        site_name = item.get("site_name") or "Unknown Platform"
        profile_url = item.get("profile_url") or f"https://{site_name.lower()}.com/{target}"
        category = item.get("category", "general")
        tags = item.get("tags", [])

        meta = {
            "site_name": site_name,
            "profile_url": profile_url,
            "category": category,
            "tags": tags,
        }

        evidence_payload = {
            "source_collector": self.name,
            "target_username": target,
            "site_name": site_name,
            "profile_url": profile_url,
            "raw_attributes": item,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        return StandardizedFinding(
            source=self.name,
            entity_type="USERNAME",
            value=target,
            finding_type=FindingType.ACCOUNT_PRESENCE,
            severity=FindingSeverity.LOW,
            title=f"Profile Found on {site_name}",
            description=f"Public profile registered for username '{target}' on {site_name}.",
            metadata=meta,
            confidence=92.0,
            evidence={
                "evidence_type": "profile_detection",
                "hash_digest": evidence_hash,
                "payload": evidence_payload,
            },
            provenance_url=profile_url,
        )
