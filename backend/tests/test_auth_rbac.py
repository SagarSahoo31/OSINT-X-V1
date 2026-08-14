"""Tests for Authentication, JWT Security, Audit Logs, and RBAC."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


def test_password_hashing():
    """Verify bcrypt hashing and verification."""
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_lifecycle():
    """Verify JWT encoding, decoding, and subject retrieval."""
    token = create_access_token(subject="usr-12345", role="ADMIN")
    payload = decode_access_token(token)
    assert payload["sub"] == "usr-12345"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_auth_register_and_login_api(async_client: AsyncClient, async_db_session: AsyncSession):
    """Test user registration and login flow."""
    # 1. Register
    reg_payload = {
        "email": "ciso@company.org",
        "username": "ciso_officer",
        "password": "SecurePassword2026!",
        "full_name": "Chief Information Security Officer",
        "role": "ADMIN",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["username"] == "ciso_officer"
    assert user_data["role"] == "ADMIN"

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "ciso_officer", "password": "SecurePassword2026!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Access Protected /me endpoint
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "ciso@company.org"
