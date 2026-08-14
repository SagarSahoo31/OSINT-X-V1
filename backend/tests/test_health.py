"""Tests for health check, versioning, and API router endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """Test top-level /api/health endpoint."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "OSINT-X"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_version_endpoint(async_client: AsyncClient):
    """Test /api/version capability endpoint."""
    response = await async_client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "OSINT-X"
    assert "capabilities" in data
    assert "target_validation" in data["capabilities"]


@pytest.mark.asyncio
async def test_v1_health_endpoint(async_client: AsyncClient):
    """Test /api/v1/health endpoint."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
