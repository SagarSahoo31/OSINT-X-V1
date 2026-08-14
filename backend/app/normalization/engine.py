"""Normalization engine translating heterogeneous collector findings into canonical entities."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from app.collectors.base import StandardizedFinding
from app.core.constants import EntityType
from app.normalization.canonicalizer import Canonicalizer
from app.normalization.deduplicator import Deduplicator
from app.schemas.entity import EntityCreate
from app.schemas.finding import FindingCreate, EvidenceCreate


class NormalizationEngine:
    """Transforms raw and standardized collector findings into canonical database entities and findings."""

    @classmethod
    def process_findings(
        cls,
        investigation_id: str,
        findings: List[StandardizedFinding],
        collector_job_id: str = None,
    ) -> Tuple[List[EntityCreate], List[FindingCreate]]:
        """
        Extracts canonical entities and findings from standardized collector outputs.
        Returns: (deduplicated_entities, findings_to_save)
        """
        raw_entities: List[EntityCreate] = []
        created_findings: List[FindingCreate] = []

        for f in findings:
            # 1. Map string entity type to EntityType enum
            try:
                e_type = EntityType(f.entity_type.upper())
            except ValueError:
                e_type = EntityType.ORGANIZATION

            # 2. Canonicalize entity value
            norm_val, disp_val, meta = Canonicalizer.canonicalize(f.value, e_type)

            # 3. Create EntityCreate DTO
            provenance_record = {
                "tool": f.source,
                "confidence": f.confidence,
                "timestamp": f.timestamp.isoformat(),
                "provenance_url": f.provenance_url,
            }
            entity_dto = EntityCreate(
                investigation_id=investigation_id,
                entity_type=e_type,
                normalized_value=norm_val,
                display_value=disp_val,
                confidence=f.confidence,
                meta_info=meta,
                source_provenance=[provenance_record],
            )
            raw_entities.append(entity_dto)

            # 4. Create FindingCreate DTO
            finding_dto = FindingCreate(
                investigation_id=investigation_id,
                collector_job_id=collector_job_id,
                source_tool=f.source,
                finding_type=f.finding_type,
                severity=f.severity,
                title=f.title,
                description=f.description,
                raw_data=f.metadata,
                normalized_data={
                    "canonical_value": norm_val,
                    "display_value": disp_val,
                    "entity_type": e_type.value,
                    "extracted_metadata": meta,
                },
                confidence=f.confidence,
                observed_at=f.timestamp,
            )
            created_findings.append(finding_dto)

        # 5. Deduplicate and corroborate entities
        deduped_entities = Deduplicator.deduplicate_entities(raw_entities)

        return deduped_entities, created_findings
