"""Master correlation engine evaluating explainable relationship heuristics."""

from typing import Dict, List
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.correlation.rules.dns_ip_rule import DomainResolvesToIPRule
from app.correlation.rules.email_domain_rule import EmailDomainMatchRule
from app.correlation.rules.subdomain_rule import SubdomainOfRule
from app.correlation.rules.technology_rule import TechnologyUsageRule
from app.correlation.rules.username_email_rule import UsernameEmailCorrelationRule
from app.schemas.entity import EntityCreate, RelationshipCreate


class CorrelationEngine:
    """Orchestrates deterministic correlation rules and produces explainable relationship graphs."""

    def __init__(self, rules: List[BaseCorrelationRule] = None) -> None:
        self.rules: List[BaseCorrelationRule] = rules or [
            SubdomainOfRule(),
            DomainResolvesToIPRule(),
            EmailDomainMatchRule(),
            UsernameEmailCorrelationRule(),
            TechnologyUsageRule(),
        ]

    def correlate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        """
        Runs all correlation rules across entities and deduplicates relationships.
        """
        all_relationships: List[RelationshipCreate] = []
        seen_keys = set()

        for rule in self.rules:
            try:
                emitted = rule.evaluate(entities, investigation_id)
                for rel in emitted:
                    key = (rel.source_entity_id, rel.target_entity_id, rel.relationship_type)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_relationships.append(rel)
            except Exception:
                # Rule failure should not interrupt other rules
                continue

        return all_relationships


correlation_engine = CorrelationEngine()
