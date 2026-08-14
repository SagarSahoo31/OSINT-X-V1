"""Continuous monitoring and investigation state delta comparison service."""

from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.models.risk import RiskScore


class MonitoringService:
    """Computes asset deltas, DNS drift, and risk score changes between scans."""

    @classmethod
    async def compare_scans(
        cls,
        db: AsyncSession,
        baseline_inv_id: str,
        current_inv_id: str,
    ) -> Dict[str, Any]:
        """
        Compares baseline and current scans for the same target asset to detect drift.
        """
        # Fetch entities for both scans
        base_entities_stmt = select(Entity).where(Entity.investigation_id == baseline_inv_id)
        base_entities = (await db.execute(base_entities_stmt)).scalars().all()
        base_ent_map = {(e.entity_type.value, e.normalized_value): e for e in base_entities}

        curr_entities_stmt = select(Entity).where(Entity.investigation_id == current_inv_id)
        curr_entities = (await db.execute(curr_entities_stmt)).scalars().all()
        curr_ent_map = {(e.entity_type.value, e.normalized_value): e for e in curr_entities}

        # Compute added and removed entities
        added_keys = set(curr_ent_map.keys()) - set(base_ent_map.keys())
        removed_keys = set(base_ent_map.keys()) - set(curr_ent_map.keys())
        persistent_keys = set(curr_ent_map.keys()) & set(base_ent_map.keys())

        added_entities = [
            {"type": k[0], "value": k[1], "display": curr_ent_map[k].display_value}
            for k in added_keys
        ]
        removed_entities = [
            {"type": k[0], "value": k[1], "display": base_ent_map[k].display_value}
            for k in removed_keys
        ]

        # Fetch findings for both scans
        base_find_stmt = select(Finding).where(Finding.investigation_id == baseline_inv_id)
        base_findings = (await db.execute(base_find_stmt)).scalars().all()

        curr_find_stmt = select(Finding).where(Finding.investigation_id == current_inv_id)
        curr_findings = (await db.execute(curr_find_stmt)).scalars().all()

        # Fetch risk scores
        base_risk_stmt = select(RiskScore).where(RiskScore.investigation_id == baseline_inv_id).order_by(RiskScore.calculated_at.desc())
        base_risk = (await db.execute(base_risk_stmt)).scalars().first()
        base_score = base_risk.overall_score if base_risk else 0.0

        curr_risk_stmt = select(RiskScore).where(RiskScore.investigation_id == current_inv_id).order_by(RiskScore.calculated_at.desc())
        curr_risk = (await db.execute(curr_risk_stmt)).scalars().first()
        curr_score = curr_risk.overall_score if curr_risk else 0.0

        risk_delta = round(curr_score - base_score, 1)

        return {
            "baseline_investigation_id": baseline_inv_id,
            "current_investigation_id": current_inv_id,
            "risk_assessment": {
                "baseline_score": base_score,
                "current_score": curr_score,
                "risk_delta": risk_delta,
                "trend": "INCREASED" if risk_delta > 0 else ("DECREASED" if risk_delta < 0 else "UNCHANGED"),
            },
            "asset_changes": {
                "new_assets_count": len(added_entities),
                "removed_assets_count": len(removed_entities),
                "persistent_assets_count": len(persistent_keys),
                "new_assets": added_entities,
                "removed_assets": removed_entities,
            },
            "findings_summary": {
                "baseline_total": len(base_findings),
                "current_total": len(curr_findings),
                "delta": len(curr_findings) - len(base_findings),
            },
        }

    @classmethod
    async def get_investigation_timeline(
        cls,
        db: AsyncSession,
        investigation_id: str,
    ) -> List[Dict[str, Any]]:
        """Extracts chronological discovery timeline events for an investigation."""
        events: List[Dict[str, Any]] = []

        # 1. Fetch investigation
        inv_stmt = select(Investigation).where(Investigation.id == investigation_id)
        inv = (await db.execute(inv_stmt)).scalar_one_or_none()
        if inv:
            events.append({
                "timestamp": inv.created_at.isoformat(),
                "event_type": "INVESTIGATION_CREATED",
                "title": f"Investigation Initialized: {inv.title}",
                "description": f"Target: {inv.target_input} ({inv.target_type.value})",
            })

        # 2. Fetch findings
        f_stmt = select(Finding).where(Finding.investigation_id == investigation_id).order_by(Finding.observed_at.asc())
        findings = (await db.execute(f_stmt)).scalars().all()
        for f in findings:
            events.append({
                "timestamp": f.observed_at.isoformat(),
                "event_type": "FINDING_DISCOVERED",
                "title": f.title,
                "description": f.description or f"Observed by {f.source_tool}",
                "severity": f.severity.value,
                "source": f.source_tool,
            })

        # Sort all events chronologically
        events.sort(key=lambda x: x["timestamp"])
        return events
