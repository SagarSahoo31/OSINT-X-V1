"""AI Analyst endpoints for structured evidence synthesis."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ollama_client import ollama_analyst
from app.core.database import get_db
from app.models.entity import Entity, Relationship
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.models.risk import RiskScore

router = APIRouter(prefix="/investigations/{investigation_id}/ai", tags=["AI Analyst"])


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_investigation_with_ai(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generates structured evidence-grounded AI security assessment using local Ollama model."""
    inv_stmt = select(Investigation).where(Investigation.id == investigation_id)
    inv = (await db.execute(inv_stmt)).scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    e_stmt = select(Entity).where(Entity.investigation_id == investigation_id)
    entities = [e.to_dict() for e in (await db.execute(e_stmt)).scalars().all()]

    r_stmt = select(Relationship).where(Relationship.investigation_id == investigation_id)
    relationships = [r.to_dict() for r in (await db.execute(r_stmt)).scalars().all()]

    f_stmt = select(Finding).where(Finding.investigation_id == investigation_id)
    findings = [f.to_dict() for f in (await db.execute(f_stmt)).scalars().all()]

    risk_stmt = select(RiskScore).where(RiskScore.investigation_id == investigation_id).order_by(RiskScore.calculated_at.desc())
    latest_risk = (await db.execute(risk_stmt)).scalars().first()
    risk_score = latest_risk.overall_score if latest_risk else 0.0

    analysis_res = await ollama_analyst.analyze_investigation(
        target=inv.target_input,
        target_type=inv.target_type.value,
        entities=entities,
        relationships=relationships,
        findings=findings,
        risk_score=risk_score,
    )

    return {
        "investigation_id": investigation_id,
        "target": inv.target_input,
        "risk_score": risk_score,
        **analysis_res,
    }
