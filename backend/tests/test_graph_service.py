"""Tests for Graph projection service and Graph API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EntityType, RelationshipType, TargetType
from app.graph.sync_service import GraphSyncService
from app.models.entity import Entity, Relationship
from app.models.investigation import Investigation


@pytest.mark.asyncio
async def test_get_graph_data_from_db(async_db_session: AsyncSession):
    """Test extracting node-link graph directly from relational database."""
    inv = Investigation(
        title="Graph Test",
        target_input="graph.target.com",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
    )
    async_db_session.add(inv)
    await async_db_session.flush()

    e1 = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.DOMAIN,
        normalized_value="graph.target.com",
        display_value="graph.target.com",
        confidence=100.0,
    )
    e2 = Entity(
        investigation_id=inv.id,
        entity_type=EntityType.IP,
        normalized_value="198.51.100.2",
        display_value="198.51.100.2",
        confidence=90.0,
    )
    async_db_session.add_all([e1, e2])
    await async_db_session.flush()

    rel = Relationship(
        investigation_id=inv.id,
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type=RelationshipType.RESOLVES_TO,
        confidence=90.0,
        reason="A Record",
        source_tool="dns",
    )
    async_db_session.add(rel)
    await async_db_session.commit()

    graph = await GraphSyncService.get_graph_data_from_db(async_db_session, inv.id)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.edges[0].source == e1.id
    assert graph.edges[0].target == e2.id
    assert graph.edges[0].label == RelationshipType.RESOLVES_TO


@pytest.mark.asyncio
async def test_graph_api_endpoint(async_client: AsyncClient, async_db_session: AsyncSession):
    """Test GET /api/v1/investigations/{id}/graph."""
    inv = Investigation(
        title="Graph API Test",
        target_input="target.org",
        target_type=TargetType.DOMAIN,
        is_authorized=True,
    )
    async_db_session.add(inv)
    await async_db_session.commit()

    response = await async_client.get(f"/api/v1/investigations/{inv.id}/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
