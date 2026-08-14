"""OSINT-X API Package."""

from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.investigations import router as investigations_router
from app.api.graph import router as graph_router
from app.api.reports import router as reports_router
from app.api.ai import router as ai_router
from app.api.monitoring import router as monitoring_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["System Health"])
api_router.include_router(auth_router)
api_router.include_router(investigations_router)
api_router.include_router(graph_router)
api_router.include_router(reports_router)
api_router.include_router(ai_router)
api_router.include_router(monitoring_router)
