"""Correlation rule linking subdomains to parent registered domains."""

from typing import List
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.core.constants import EntityType, RelationshipType
from app.schemas.entity import EntityCreate, RelationshipCreate


class SubdomainOfRule(BaseCorrelationRule):
    """Detects when a SUBDOMAIN belongs to a registered root DOMAIN."""

    name = "subdomain_of_root"
    description = "Links discovered subdomains to their root registered domain"

    def evaluate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        relationships: List[RelationshipCreate] = []

        domains = {e.normalized_value: e for e in entities if e.entity_type == EntityType.DOMAIN}
        subdomains = [e for e in entities if e.entity_type in (EntityType.SUBDOMAIN, EntityType.DOMAIN) and e.meta_info.get("is_subdomain")]

        for sub in subdomains:
            reg_domain = sub.meta_info.get("registered_domain")
            if reg_domain and reg_domain in domains and sub.normalized_value != reg_domain:
                parent_entity = domains[reg_domain]
                relationships.append(
                    RelationshipCreate(
                        investigation_id=investigation_id,
                        source_entity_id=sub.normalized_value,  # ID resolved by correlation engine
                        target_entity_id=parent_entity.normalized_value,
                        relationship_type=RelationshipType.SUBDOMAIN_OF,
                        confidence=98.0,
                        reason=f"High-confidence DNS hierarchy: '{sub.normalized_value}' is a subdomain of root domain '{reg_domain}'.",
                        source_tool="correlation_engine",
                        evidence={
                            "subdomain": sub.normalized_value,
                            "registered_domain": reg_domain,
                            "tld": sub.meta_info.get("tld"),
                        },
                    )
                )

        return relationships
