from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from py_domain.permissions import Permission


@dataclass(slots=True)
class UserContext:
    user_id: str
    user_name: str
    permissions: list[str]


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
    x_user_permissions: str | None = Header(default=None),
) -> UserContext:
    if not x_user_id:
        return UserContext(
            user_id="u_admin",
            user_name="System Admin",
            permissions=[permission.value for permission in Permission],
        )

    permissions = [item.strip() for item in (x_user_permissions or "").split(",") if item.strip()]
    return UserContext(
        user_id=x_user_id,
        user_name=x_user_name or "Unknown User",
        permissions=permissions,
    )


def require_permission(permission: Permission) -> Callable[[UserContext], UserContext]:
    def dependency(user: UserContext = Depends(get_current_user)) -> UserContext:
        if permission.value not in user.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency
