"""Neo4j graph database client and query runner."""

from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver

from app.core.config import settings
from app.core.logging import logger


class Neo4jClient:
    """Async Neo4j driver client managing connection pooling and Cypher execution."""

    def __init__(self) -> None:
        self._driver: Optional[AsyncDriver] = None

    def get_driver(self) -> AsyncDriver:
        """Initializes or returns active AsyncDriver."""
        if not self._driver:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
        return self._driver

    async def close(self) -> None:
        """Closes active Neo4j driver connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def health_check(self) -> bool:
        """Verifies if Neo4j instance is reachable."""
        try:
            driver = self.get_driver()
            await driver.verify_connectivity()
            return True
        except Exception as exc:
            logger.debug("Neo4j connectivity check failed: %s", str(exc))
            return False

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Executes a parameterized Cypher query and returns record dicts."""
        driver = self.get_driver()
        async with driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records


neo4j_client = Neo4jClient()
