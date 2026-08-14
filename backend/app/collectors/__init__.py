"""Collectors package auto-registering all built-in OSINT adapters."""

from app.collectors.base import BaseCollector, RawCollectorResult, StandardizedFinding
from app.collectors.runner import run_subprocess_sandboxed
from app.collectors.registry import CollectorRegistry, registry

from app.collectors.holehe.adapter import HoleheCollector
from app.collectors.maigret.adapter import MaigretCollector
from app.collectors.amass.adapter import AmassCollector
from app.collectors.dns.adapter import DNSCollector
from app.collectors.httpx.adapter import HTTPXCollector
from app.collectors.whatweb.adapter import WhatWebCollector
from app.collectors.crtsh.adapter import CrtshCollector

# Register all built-in collectors into global registry singleton
registry.register(HoleheCollector())
registry.register(MaigretCollector())
registry.register(AmassCollector())
registry.register(DNSCollector())
registry.register(HTTPXCollector())
registry.register(WhatWebCollector())
registry.register(CrtshCollector())

__all__ = [
    "BaseCollector",
    "RawCollectorResult",
    "StandardizedFinding",
    "CollectorRegistry",
    "registry",
    "run_subprocess_sandboxed",
    "HoleheCollector",
    "MaigretCollector",
    "AmassCollector",
    "DNSCollector",
    "HTTPXCollector",
    "WhatWebCollector",
    "CrtshCollector",
]
