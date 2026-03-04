from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import SSOState


@dataclass(slots=True)
class SSOIdentity:
    user_id: str
    user_name: str
    email: str | None


async def create_login_state(session: AsyncSession, redirect_uri: str) -> str:
    state = secrets.token_urlsafe(24)
    session.add(SSOState(state=state, redirect_uri=redirect_uri))
    await session.flush()
    return state


async def consume_login_state(session: AsyncSession, state: str) -> SSOState:
    state_row = await session.get(SSOState, state)
    if state_row is None or state_row.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")

    state_row.used_at = datetime.now(tz=UTC)
    await session.flush()
    return state_row


def build_auth_url(state: str) -> str:
    settings = get_settings()
    if settings.sso_mode == "mock":
        return f"{settings.api_prefix}/auth/callback?code=mock:{settings.sso_mock_default_user}&state={state}"

    return (
        f"{settings.sso_issuer_url}/authorize"
        f"?client_id={settings.sso_client_id}"
        f"&response_type=code"
        f"&redirect_uri={settings.sso_redirect_uri}"
        f"&scope=openid%20profile%20email"
        f"&state={state}"
    )


async def resolve_identity_from_code(code: str) -> SSOIdentity:
    settings = get_settings()
    if settings.sso_mode != "mock":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OIDC token exchange is not implemented in this scaffold",
        )

    if not code.startswith("mock:"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mock code")

    user_id = code.split(":", 1)[1].strip()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mock user id")

    user_name = {
        "u_admin": "System Admin",
        "u_auditor": "Audit User",
        "u_employee": "Employee User",
    }.get(user_id, user_id)

    return SSOIdentity(user_id=user_id, user_name=user_name, email=f"{user_id}@internal.local")
