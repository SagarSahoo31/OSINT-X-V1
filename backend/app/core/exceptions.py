"""Domain exception hierarchy for OSINT-X."""

from typing import Any, Optional


class OSINTXException(Exception):
    """Base exception for all domain errors within OSINT-X."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TargetValidationError(OSINTXException):
    """Raised when an input target fails syntax validation or violates safety constraints."""
    pass


class TargetAuthorizationError(OSINTXException):
    """Raised when an active scan is requested without required target authorization confirmation."""
    pass


class CollectorNotFoundError(OSINTXException):
    """Raised when a requested collector adapter is not registered."""
    pass


class CollectorExecutionError(OSINTXException):
    """Raised when an OSINT tool adapter subprocess fails or encounters fatal errors."""
    pass


class CollectorTimeoutError(CollectorExecutionError):
    """Raised when a collector execution exceeds the configured timeout limit."""
    pass


class NormalizationError(OSINTXException):
    """Raised when raw finding data cannot be parsed into the canonical model."""
    pass


class CorrelationError(OSINTXException):
    """Raised during graph relationship inference or correlation engine failures."""
    pass


class RiskScoringError(OSINTXException):
    """Raised during exposure risk score calculation."""
    pass


class EntityNotFoundError(OSINTXException):
    """Raised when an entity is not found in the database."""
    pass


class InvestigationNotFoundError(OSINTXException):
    """Raised when an investigation is not found in the database."""
    pass


class DatabaseSyncError(OSINTXException):
    """Raised when syncing relational data to the Neo4j graph fails."""
    pass
