"""Correlation rule linking usernames to email addresses based on shared local parts or hints."""

from typing import List
from app.correlation.rules.base_rule import BaseCorrelationRule
from app.core.constants import EntityType, RelationshipType
from app.schemas.entity import EntityCreate, RelationshipCreate


class UsernameEmailCorrelationRule(BaseCorrelationRule):
    """Correlates usernames and emails based on matching handles or discovery hints."""

    name = "username_email_handle_match"
    description = "Correlates usernames to emails sharing identical handle stems"

    def evaluate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        relationships: List[RelationshipCreate] = []
        usernames = {e.normalized_value: e for e in entities if e.entity_type == EntityType.USERNAME}
        emails = [e for e in entities if e.entity_type == EntityType.EMAIL]

        for email in emails:
            local_part = email.normalized_value.split("@")[0]
            if local_part in usernames:
                relationships.append(
                    RelationshipCreate(
                        investigation_id=investigation_id,
                        source_entity_id=usernames[local_part].normalized_value,
                        target_entity_id=email.normalized_value,
                        relationship_type=RelationshipType.POSSIBLY_BELONGS_TO,
                        confidence=75.0,
                        reason=f"Probable identity association: username '{local_part}' matches local handle stem of email '{email.normalized_value}'.",
                        source_tool="correlation_engine",
                        evidence={"username": local_part, "email": email.normalized_value},
                    )
                )

        return relationships
