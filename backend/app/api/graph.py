"""Graph intelligence endpoints providing node-link topology and Neo4j sync."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.graph.sync_service import GraphSyncService
from app.schemas.entity import GraphData

router = APIRouter(prefix="/investigations/{investigation_id}/graph", tags=["Intelligence Graph"])


@router.get("", response_model=GraphData)
async def get_investigation_graph(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> GraphData:
    """Returns interactive node-link graph projection formatted for visual canvas."""
    return await GraphSyncService.get_graph_data_from_db(db=db, investigation_id=investigation_id)


@router.post("/sync", response_model=Dict[str, Any])
async def sync_investigation_graph(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Triggers on-demand sync of PostgreSQL entities/relationships to Neo4j."""
    success = await GraphSyncService.sync_investigation_to_neo4j(db=db, investigation_id=investigation_id)
    return {
        "investigation_id": investigation_id,
        "synced": success,
        "status": "synchronized" if success else "neo4j_unavailable_fallback_active",
    }
