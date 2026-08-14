"""Correlation rule linking technology stack items to hosting domains or URLs."""

from typing import List
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.core.constants import EntityType, RelationshipType
from app.schemas.entity import EntityCreate, RelationshipCreate


class TechnologyUsageRule(BaseCorrelationRule):
    """Links detected technology stack components to the hosting domain/URL asset."""

    name = "technology_usage"
    description = "Associates technology components to the assets they are deployed on"

    def evaluate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        relationships: List[RelationshipCreate] = []
        host_entities = [e for e in entities if e.entity_type in (EntityType.DOMAIN, EntityType.SUBDOMAIN, EntityType.URL)]
        tech_entities = {e.normalized_value: e for e in entities if e.entity_type == EntityType.TECHNOLOGY}

        for host in host_entities:
            detected_techs = host.meta_info.get("detected_technologies", [])
            for tech_name in detected_techs:
                norm_tech = tech_name.lower().strip()
                if norm_tech in tech_entities:
                    relationships.append(
                        RelationshipCreate(
                            investigation_id=investigation_id,
                            source_entity_id=host.normalized_value,
                            target_entity_id=norm_tech,
                            relationship_type=RelationshipType.USES,
                            confidence=90.0,
                            reason=f"Technology detection: '{host.normalized_value}' uses component '{tech_name}'.",
                            source_tool="correlation_engine",
                            evidence={"host": host.normalized_value, "technology": tech_name},
                        )
                    )

        return relationships
