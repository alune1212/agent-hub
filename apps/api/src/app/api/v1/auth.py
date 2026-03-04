from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from py_common import build_trace_id
from py_domain.events import OutboxEventPayload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.security import UserContext, create_access_token, get_current_user
from app.services.iam import ensure_default_role, get_user_profile, upsert_user
from app.services.outbox import append_outbox_event
from app.services.sso import (
    build_auth_url,
    consume_login_state,
    create_login_state,
    resolve_identity_from_code,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(
    redirect_uri: str = "/",
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    async with session.begin():
        state = await create_login_state(session, redirect_uri=redirect_uri)

    return {
        "provider": "oidc",
        "mode": get_settings().sso_mode,
        "state": state,
        "auth_url": build_auth_url(state),
    }


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    session: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    trace_id = build_trace_id()

    async with session.begin():
        await consume_login_state(session, state)
        identity = await resolve_identity_from_code(code)
        await upsert_user(
            session,
            user_id=identity.user_id,
            user_name=identity.user_name,
            email=identity.email,
        )
        await ensure_default_role(session, user_id=identity.user_id)

        audit_payload = OutboxEventPayload(
            event_type="auth.sso.login",
            aggregate_type="user",
            aggregate_id=identity.user_id,
            actor_id=identity.user_id,
            actor_name=identity.user_name,
            action="auth.sso.login",
            detail={"state": state},
        )
        await append_outbox_event(session, payload=audit_payload, trace_id=trace_id)

        profile = await get_user_profile(session, identity.user_id)

    token = create_access_token(profile.user_id, profile.user_name)
    settings = get_settings()

    response = JSONResponse(
        {
            "message": "sso callback accepted",
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expires_minutes * 60,
            "user": {
                "user_id": profile.user_id,
                "user_name": profile.user_name,
                "email": profile.email,
                "roles": profile.roles,
                "permissions": profile.permissions,
            },
        }
    )
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.jwt_expires_minutes * 60,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("access_token")
    return {"message": "logout success"}


@router.get("/me")
async def me(
    user: UserContext = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    try:
        profile = await get_user_profile(session, user.user_id)
        return {
            "user_id": profile.user_id,
            "user_name": profile.user_name,
            "email": profile.email,
            "roles": profile.roles,
            "permissions": profile.permissions,
        }
    except Exception:
        return {
            "user_id": user.user_id,
            "user_name": user.user_name,
            "email": None,
            "roles": user.roles,
            "permissions": user.permissions,
        }
