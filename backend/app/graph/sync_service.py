"""Graph projection and PostgreSQL-to-Neo4j synchronization service."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import logger
from app.graph.client import neo4j_client
from app.models.entity import Entity, Relationship
from app.models.investigation import Investigation
from app.schemas.entity import GraphData, GraphEdge, GraphNode


class GraphSyncService:
    """Synchronizes PostgreSQL relational intelligence into Neo4j graph database."""

    @classmethod
    async def get_graph_data_from_db(
        cls,
        db: AsyncSession,
        investigation_id: str,
    ) -> GraphData:
        """
        Extracts entities and relationships from PostgreSQL and constructs GraphData payload.
        Guarantees graph visualization even if Neo4j is offline.
        """
        # Fetch entities
        e_stmt = select(Entity).where(Entity.investigation_id == investigation_id)
        e_res = await db.execute(e_stmt)
        entities = e_res.scalars().all()

        # Fetch relationships
        r_stmt = select(Relationship).where(Relationship.investigation_id == investigation_id)
        r_res = await db.execute(r_stmt)
        relationships = r_res.scalars().all()

        nodes: List[GraphNode] = []
        for ent in entities:
            nodes.append(
                GraphNode(
                    id=ent.id,
                    label=ent.display_value,
                    entity_type=ent.entity_type,
                    confidence=ent.confidence,
                    meta_info=ent.meta_info,
                )
            )

        edges: List[GraphEdge] = []
        for rel in relationships:
            edges.append(
                GraphEdge(
                    id=rel.id,
                    source=rel.source_entity_id,
                    target=rel.target_entity_id,
                    label=rel.relationship_type,
                    confidence=rel.confidence,
                    reason=rel.reason,
                    source_tool=rel.source_tool,
                )
            )

        return GraphData(nodes=nodes, edges=edges)

    @classmethod
    async def sync_investigation_to_neo4j(
        cls,
        db: AsyncSession,
        investigation_id: str,
    ) -> bool:
        """
        Projects PostgreSQL entities and relationships into Neo4j nodes and edges.
        """
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            logger.info("Neo4j is not reachable; graph sync skipped.")
            return False

        graph_data = await cls.get_graph_data_from_db(db, investigation_id)

        try:
            # 1. Upsert Nodes
            for node in graph_data.nodes:
                cypher_node = f"""
                MERGE (n:Entity {{id: $id, investigation_id: $inv_id}})
                SET n.label = $label,
                    n.entity_type = $entity_type,
                    n.confidence = $confidence
                """
                await neo4j_client.execute_query(
                    cypher_node,
                    {
                        "id": node.id,
                        "inv_id": investigation_id,
                        "label": node.label,
                        "entity_type": node.entity_type.value,
                        "confidence": node.confidence,
                    },
                )

            # 2. Upsert Edges
            for edge in graph_data.edges:
                cypher_edge = f"""
                MATCH (s:Entity {{id: $source_id, investigation_id: $inv_id}})
                MATCH (t:Entity {{id: $target_id, investigation_id: $inv_id}})
                MERGE (s)-[r:{edge.label.value}]->(t)
                SET r.id = $edge_id,
                    r.confidence = $confidence,
                    r.reason = $reason,
                    r.source_tool = $source_tool
                """
                await neo4j_client.execute_query(
                    cypher_edge,
                    {
                        "source_id": edge.source,
                        "target_id": edge.target,
                        "inv_id": investigation_id,
                        "edge_id": edge.id,
                        "confidence": edge.confidence,
                        "reason": edge.reason,
                        "source_tool": edge.source_tool,
                    },
                )

            logger.info("Synced %d nodes and %d edges to Neo4j for investigation %s", len(graph_data.nodes), len(graph_data.edges), investigation_id)
            return True

        except Exception as exc:
            logger.warning("Neo4j sync failed for investigation %s: %s", investigation_id, str(exc))
            return False
