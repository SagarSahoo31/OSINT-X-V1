"""Monitoring and timeline comparison endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.monitoring_service import MonitoringService

router = APIRouter(tags=["Monitoring & Timeline"])


@router.get("/monitoring/compare", response_model=Dict[str, Any])
async def compare_scans(
    baseline_id: str = Query(..., description="Baseline investigation ID"),
    current_id: str = Query(..., description="Current investigation ID"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Compares two scans to detect added assets, removed services, and risk score drift."""
    return await MonitoringService.compare_scans(
        db=db,
        baseline_inv_id=baseline_id,
        current_inv_id=current_id,
    )


@router.get("/investigations/{investigation_id}/timeline", response_model=List[Dict[str, Any]])
async def get_investigation_timeline(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Returns chronological timeline of discoveries and findings for an investigation."""
    return await MonitoringService.get_investigation_timeline(
        db=db,
        investigation_id=investigation_id,
    )
