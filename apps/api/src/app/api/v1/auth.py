from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import UserContext, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login() -> dict[str, str]:
    return {
        "message": "redirect to enterprise sso",
        "provider": "oidc",
    }


@router.get("/callback")
async def callback(code: str | None = None) -> dict[str, str | None]:
    return {
        "message": "sso callback accepted",
        "code": code,
    }


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"message": "logout success"}


@router.get("/me")
async def me(user: UserContext = Depends(get_current_user)) -> dict[str, object]:
    return {
        "user_id": user.user_id,
        "user_name": user.user_name,
        "permissions": user.permissions,
    }
