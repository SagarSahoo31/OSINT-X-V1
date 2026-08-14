"""Collector registry for registering, discovering, and dispatching OSINT adapters."""

from typing import Dict, List, Optional
from app.collectors.base import BaseCollector
from app.core.constants import CollectorName, TargetType
from app.core.exceptions import CollectorNotFoundError


class CollectorRegistry:
    """Singleton catalog maintaining all available OSINT collector adapters."""

    def __init__(self) -> None:
        self._collectors: Dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        """Registers a collector adapter instance."""
        self._collectors[collector.name.lower()] = collector

    def get(self, name: str) -> BaseCollector:
        """Retrieves a collector adapter by name."""
        name_lower = name.lower()
        if name_lower not in self._collectors:
            raise CollectorNotFoundError(f"Collector adapter '{name}' is not registered.")
        return self._collectors[name_lower]

    def list_for_target_type(self, target_type: TargetType) -> List[BaseCollector]:
        """Returns all registered collectors that support a specific target type."""
        return [
            col
            for col in self._collectors.values()
            if target_type in col.supported_target_types
        ]

    def list_all(self) -> List[BaseCollector]:
        """Returns all registered collectors."""
        return list(self._collectors.values())


registry = CollectorRegistry()
