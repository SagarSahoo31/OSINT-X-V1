"""Authentication endpoints for registration, login, token refresh, and user profile."""

from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, log_audit_event, require_role
from app.core.constants import UserRole
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Registers a new user account."""
    # Check email duplicate
    stmt = select(User).where((User.email == payload.email) | (User.username == payload.username))
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or username already exists.",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await log_audit_event(
        db=db,
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=user.id,
        user_id=user.id,
        details={"username": user.username, "role": user.role.value},
        ip_address=request.client.host if request.client else None,
    )

    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticates user credentials and returns JWT Bearer token."""
    stmt = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(subject=user.id, role=user.role.value)

    client_ip = request.client.host if request and request.client else None
    await log_audit_event(
        db=db,
        action="USER_LOGIN_SUCCESS",
        resource_type="USER",
        resource_id=user.id,
        user_id=user.id,
        details={"username": user.username},
        ip_address=client_ip,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(require_role(UserRole.READONLY)),
) -> UserRead:
    """Returns the profile of the currently authenticated user."""
    return UserRead.model_validate(current_user)
