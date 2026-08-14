"""FastAPI dependency injection utilities for authentication, RBAC, and audit logging."""

from typing import Callable, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import UserRole
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import AuditLog, User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Extracts and validates current authenticated user from Bearer token."""
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            return None
    except ValueError:
        return None

    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


def require_role(required_role: UserRole) -> Callable:
    """Dependency factory enforcing RBAC minimum permission level."""
    async def role_checker(
        current_user: Optional[User] = Depends(get_current_user),
    ) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials were not provided.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if current_user.is_superuser or current_user.role == UserRole.ADMIN:
            return current_user

        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires '{required_role.value}' role permissions.",
            )
        return current_user

    return role_checker


async def log_audit_event(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Helper creating immutable security audit records."""
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        details=details or {},
    )
    db.add(audit_entry)
    await db.commit()
