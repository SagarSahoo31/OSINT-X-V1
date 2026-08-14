"""Correlation rule linking email entities to domain entities."""

from typing import List
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.core.constants import EntityType, RelationshipType
from app.schemas.entity import EntityCreate, RelationshipCreate


class EmailDomainMatchRule(BaseCorrelationRule):
    """Links an EMAIL to its parent DOMAIN organization."""

    name = "email_domain_match"
    description = "Associates an email address with its organizational domain"

    def evaluate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        relationships: List[RelationshipCreate] = []
        emails = [e for e in entities if e.entity_type == EntityType.EMAIL]
        domains = {e.normalized_value: e for e in entities if e.entity_type == EntityType.DOMAIN}

        for email in emails:
            email_domain = email.meta_info.get("domain") or email.normalized_value.split("@")[-1]
            if email_domain in domains:
                relationships.append(
                    RelationshipCreate(
                        investigation_id=investigation_id,
                        source_entity_id=email.normalized_value,
                        target_entity_id=email_domain,
                        relationship_type=RelationshipType.USES,
                        confidence=92.0,
                        reason=f"High-confidence organizational footprint: email '{email.normalized_value}' uses domain infrastructure '{email_domain}'.",
                        source_tool="correlation_engine",
                        evidence={"email": email.normalized_value, "domain": email_domain},
                    )
                )

        return relationships
