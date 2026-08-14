"""Integration tests for investigation lifecycle REST APIs."""

import pytest
from httpx import AsyncClient
from app.core.constants import InvestigationStatus, TargetType


@pytest.mark.asyncio
async def test_validate_target_api(async_client: AsyncClient):
    """Test POST /api/v1/investigations/validate-target."""
    response = await async_client.post(
        "/api/v1/investigations/validate-target",
        json={"target_input": "https://scan.target.com", "target_type": "DOMAIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["canonical_target"] == "scan.target.com"
    assert data["metadata"]["registered_domain"] == "target.com"


@pytest.mark.asyncio
async def test_create_authorized_investigation(async_client: AsyncClient):
    """Test POST /api/v1/investigations for authorized target."""
    payload = {
        "title": "Corporate Domain Perimeter",
        "description": "Authorized external footprinting",
        "target_input": "defense-corp.org",
        "target_type": "DOMAIN",
        "is_authorized": True,
        "authorization_notes": "Signed assessment agreement",
    }
    response = await async_client.post("/api/v1/investigations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Corporate Domain Perimeter"
    assert data["status"] == "QUEUED"
    assert data["is_authorized"] is True
    assert len(data["collector_jobs"]) >= 3  # Amass, DNS, HTTPX, WhatWeb, crtsh


@pytest.mark.asyncio
async def test_reject_unauthorized_investigation(async_client: AsyncClient):
    """Test that investigations without explicit authorization confirmation are rejected."""
    payload = {
        "title": "Unauthorized Scan Attempt",
        "target_input": "victim.org",
        "target_type": "DOMAIN",
        "is_authorized": False,
    }
    response = await async_client.post("/api/v1/investigations", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "TargetAuthorizationError" in data["error"] or "rejected" in data["message"].lower()


@pytest.mark.asyncio
async def test_investigation_lifecycle_crud(async_client: AsyncClient):
    """Test full CRUD, state transitions, cancellation, and deletion."""
    # 1. Create
    create_res = await async_client.post(
        "/api/v1/investigations",
        json={
            "title": "Email Exposure Check",
            "target_input": "ciso@company.org",
            "target_type": "EMAIL",
            "is_authorized": True,
        },
    )
    assert create_res.status_code == 201
    inv_id = create_res.json()["id"]

    # 2. Get by ID
    get_res = await async_client.get(f"/api/v1/investigations/{inv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["target_input"] == "ciso@company.org"

    # 3. List
    list_res = await async_client.get("/api/v1/investigations")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 4. Patch
    patch_res = await async_client.patch(
        f"/api/v1/investigations/{inv_id}",
        json={"title": "Updated Title", "status": "RUNNING"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated Title"
    assert patch_res.json()["status"] == "RUNNING"

    # 5. Cancel
    cancel_res = await async_client.post(f"/api/v1/investigations/{inv_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # 6. Delete
    del_res = await async_client.delete(f"/api/v1/investigations/{inv_id}")
    assert del_res.status_code == 204

    # Verify 404
    get_after_del = await async_client.get(f"/api/v1/investigations/{inv_id}")
    assert get_after_del.status_code == 400  # Domain exception InvestigationNotFoundError returns 400
