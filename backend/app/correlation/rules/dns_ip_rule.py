"""Correlation rule linking domains to resolved IP addresses."""

from typing import List
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.core.constants import EntityType, RelationshipType
from app.schemas.entity import EntityCreate, RelationshipCreate


class DomainResolvesToIPRule(BaseCorrelationRule):
    """Links domains and subdomains to the IP addresses they resolve to."""

    name = "domain_resolves_to_ip"
    description = "Links domains and subdomains to resolved IP addresses based on DNS observation"

    def evaluate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        relationships: List[RelationshipCreate] = []
        domain_entities = [e for e in entities if e.entity_type in (EntityType.DOMAIN, EntityType.SUBDOMAIN)]
        ip_map = {e.normalized_value: e for e in entities if e.entity_type == EntityType.IP}

        for dom in domain_entities:
            # Check if domain meta_info contains resolved IPs
            resolved_ips = dom.meta_info.get("resolved_ips", [])
            for ip_val in resolved_ips:
                if ip_val in ip_map:
                    relationships.append(
                        RelationshipCreate(
                            investigation_id=investigation_id,
                            source_entity_id=dom.normalized_value,
                            target_entity_id=ip_val,
                            relationship_type=RelationshipType.RESOLVES_TO,
                            confidence=95.0,
                            reason=f"Authoritative DNS A/AAAA record: '{dom.normalized_value}' resolves to '{ip_val}'.",
                            source_tool="correlation_engine",
                            evidence={"domain": dom.normalized_value, "resolved_ip": ip_val},
                        )
                    )

        return relationships
