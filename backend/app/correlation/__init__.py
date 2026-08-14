"""Correlation engine package for OSINT-X."""

from app.correlation.engine import CorrelationEngine, correlation_engine
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.correlation.rules.dns_ip_rule import DomainResolvesToIPRule
from app.correlation.rules.email_domain_rule import EmailDomainMatchRule
from app.correlation.rules.subdomain_rule import SubdomainOfRule
from app.correlation.rules.technology_rule import TechnologyUsageRule
from app.correlation.rules.username_email_rule import UsernameEmailCorrelationRule

__all__ = [
    "CorrelationEngine",
    "correlation_engine",
    "BaseCorrelationRule",
    "SubdomainOfRule",
    "DomainResolvesToIPRule",
    "EmailDomainMatchRule",
    "UsernameEmailCorrelationRule",
    "TechnologyUsageRule",
]
