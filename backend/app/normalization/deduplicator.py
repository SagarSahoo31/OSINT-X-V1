"""Deduplication and confidence corroboration engine."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from app.core.constants import EntityType
from app.schemas.entity import EntityCreate
from app.schemas.finding import FindingCreate, EvidenceCreate


class Deduplicator:
    """Merges duplicate findings and canonical entities while preserving full provenance."""

    @classmethod
    def deduplicate_entities(cls, raw_entities: List[EntityCreate]) -> List[EntityCreate]:
        """
        Groups entities by (entity_type, normalized_value) and combines provenance records.
        Applies a multi-source corroboration confidence boost.
        """
        entity_map: Dict[tuple, EntityCreate] = {}

        for ent in raw_entities:
            key = (ent.entity_type, ent.normalized_value)
            if key not in entity_map:
                entity_map[key] = ent
            else:
                existing = entity_map[key]
                # Merge provenance records
                existing_sources = {p.get("tool") for p in existing.source_provenance if isinstance(p, dict)}
                for prov in ent.source_provenance:
                    if isinstance(prov, dict) and prov.get("tool") not in existing_sources:
                        existing.source_provenance.append(prov)
                        existing_sources.add(prov.get("tool"))

                # Corroboration boost: each independent source boosts confidence up to 100%
                num_sources = len(existing_sources)
                if num_sources > 1:
                    boost = min(15.0 * (num_sources - 1), 20.0)
                    existing.confidence = min(100.0, max(existing.confidence, ent.confidence) + boost)

                # Merge metadata dicts
                existing.meta_info.update(ent.meta_info)

        return list(entity_map.values())
