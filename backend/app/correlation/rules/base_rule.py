"""Base correlation rule abstraction."""

from abc import ABC, abstractmethod
from typing import List
from app.schemas.entity import EntityCreate, RelationshipCreate


class BaseCorrelationRule(ABC):
    """Contract for deterministic correlation heuristics."""

    name: str = "base_rule"
    description: str = "Base correlation rule"

    @abstractmethod
    def evaluate(self, entities: List[EntityCreate], investigation_id: str) -> List[RelationshipCreate]:
        """
        Evaluates a set of normalized entities and emits explainable directed relationships.
        """
        pass
