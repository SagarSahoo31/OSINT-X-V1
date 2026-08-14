"""Health check and system telemetry endpoints."""

from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def get_health() -> Dict[str, Any]:
    """Returns platform operational health status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/version", response_model=Dict[str, Any])
async def get_version() -> Dict[str, Any]:
    """Returns application version and capability metadata."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "capabilities": [
            "target_validation",
            "collector_orchestration",
            "canonical_normalization",
            "entity_correlation",
            "exposure_risk_scoring",
            "graph_synchronization",
            "multi_format_reporting",
        ],
    }
