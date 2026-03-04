from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from jwt import InvalidTokenError
from py_domain.permissions import Permission
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from app.db.models import RolePermission, User, UserRole


@dataclass(slots=True)
class UserContext:
    user_id: str
    user_name: str
    roles: list[str]
    permissions: list[str]


def create_access_token(user_id: str, user_name: str) -> str:
    settings = get_settings()
    now = datetime.now(tz=UTC)
    expire_at = now + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {
        "sub": user_id,
        "name": user_name,
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


async def _load_user_context(session: AsyncSession, user_id: str) -> UserContext:
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    role_rows = await session.execute(select(UserRole.role_id).where(UserRole.user_id == user_id))
    roles = sorted({row[0] for row in role_rows.all()})

    permission_rows = await session.execute(
        select(RolePermission.permission_key)
        .join(UserRole, RolePermission.role_id == UserRole.role_id)
        .where(UserRole.user_id == user_id)
    )
    permissions = sorted({row[0] for row in permission_rows.all()})

    return UserContext(
        user_id=user.user_id,
        user_name=user.user_name,
        roles=roles,
        permissions=permissions,
    )


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    return authorization.split(" ", 1)[1].strip()


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    authorization: str | None = Header(default=None),
    access_token_cookie: str | None = Cookie(default=None, alias="access_token"),
    x_user_id: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
    x_user_permissions: str | None = Header(default=None),
) -> UserContext:
    settings = get_settings()

    token = _extract_bearer_token(authorization) or access_token_cookie
    if token:
        try:
            payload = decode_access_token(token)
        except InvalidTokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc

        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
        return await _load_user_context(session, subject)

    if settings.auth_allow_debug_headers:
        if x_user_id:
            try:
                return await _load_user_context(session, x_user_id)
            except Exception:
                permissions = [item.strip() for item in (x_user_permissions or "").split(",") if item.strip()]
                if not permissions:
                    permissions = [permission.value for permission in Permission]
                return UserContext(
                    user_id=x_user_id,
                    user_name=x_user_name or "Debug User",
                    roles=[],
                    permissions=permissions,
                )

        return UserContext(
            user_id=settings.sso_mock_default_user,
            user_name="System Admin",
            roles=["admin"],
            permissions=[permission.value for permission in Permission],
        )

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


def require_permission(permission: Permission | str) -> Callable[[UserContext], UserContext]:
    permission_key = permission.value if isinstance(permission, Permission) else permission

    def dependency(user: UserContext = Depends(get_current_user)) -> UserContext:
        if permission_key not in user.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency
