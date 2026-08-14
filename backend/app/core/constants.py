"""Core domain constants and enumerations for OSINT-X."""

from enum import Enum, StrEnum


class EntityType(StrEnum):
    """Supported entity categories across the intelligence pipeline."""
    PERSON = "PERSON"
    EMAIL = "EMAIL"
    USERNAME = "USERNAME"
    ORGANIZATION = "ORGANIZATION"
    DOMAIN = "DOMAIN"
    SUBDOMAIN = "SUBDOMAIN"
    IP = "IP"
    ASN = "ASN"
    URL = "URL"
    CERTIFICATE = "CERTIFICATE"
    SERVICE = "SERVICE"
    TECHNOLOGY = "TECHNOLOGY"
    BREACH = "BREACH"
    THREAT_INDICATOR = "THREAT_INDICATOR"


class RelationshipType(StrEnum):
    """Explainable relationship types linking entities."""
    OWNS = "OWNS"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    USES = "USES"
    RESOLVES_TO = "RESOLVES_TO"
    HOSTED_ON = "HOSTED_ON"
    SUBDOMAIN_OF = "SUBDOMAIN_OF"
    ISSUED_TO = "ISSUED_TO"
    DISCOVERED_FROM = "DISCOVERED_FROM"
    CONNECTED_TO = "CONNECTED_TO"
    OBSERVED_ON = "OBSERVED_ON"
    POSSIBLY_BELONGS_TO = "POSSIBLY_BELONGS_TO"


class TargetType(StrEnum):
    """Authorized target types supported by the investigation engine."""
    EMAIL = "EMAIL"
    USERNAME = "USERNAME"
    DOMAIN = "DOMAIN"
    IP = "IP"
    URL = "URL"


class InvestigationStatus(StrEnum):
    """State machine lifecycle for investigations."""
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CollectorJobStatus(StrEnum):
    """Execution status for individual collector tasks."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    SKIPPED = "SKIPPED"


class FindingSeverity(StrEnum):
    """Severity ratings for exposure findings."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingType(StrEnum):
    """Categorization of raw and normalized findings."""
    ACCOUNT_PRESENCE = "account_presence"
    DNS_RECORD = "dns_record"
    SUBDOMAIN_DISCOVERY = "subdomain_discovery"
    HTTP_ENDPOINT = "http_endpoint"
    TECHNOLOGY_STACK = "technology_stack"
    CERTIFICATE_SAN = "certificate_san"
    PORT_OPEN = "port_open"
    BREACH_ENTRY = "breach_entry"
    WHOIS_RECORD = "whois_record"
    GENERAL_OSINT = "general_osint"


class UserRole(StrEnum):
    """Role-Based Access Control definitions."""
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    AUDITOR = "AUDITOR"
    READONLY = "READONLY"


class CollectorName(StrEnum):
    """Catalog of built-in collector identifiers."""
    HOLEHE = "holehe"
    MAIGRET = "maigret"
    AMASS = "amass"
    DNS = "dns"
    HTTPX = "httpx"
    WHATWEB = "whatweb"
    CRTSH = "crtsh"
    SPIDERFOOT = "spiderfoot"
    MISP = "misp"
