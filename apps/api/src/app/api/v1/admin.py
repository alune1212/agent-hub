from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import UserContext, require_permission
from app.domain.schemas import PermissionAssignRequest, RoleAssignRequest
from py_domain.permissions import Permission

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(_: UserContext = Depends(require_permission(Permission.ADMIN_USERS_READ))) -> list[dict]:
    return [
        {"user_id": "u_admin", "name": "System Admin", "roles": ["admin"]},
        {"user_id": "u_auditor", "name": "Audit User", "roles": ["auditor"]},
    ]


@router.put("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: str,
    payload: RoleAssignRequest,
    _: UserContext = Depends(require_permission(Permission.ADMIN_USERS_WRITE)),
) -> dict[str, object]:
    return {"user_id": user_id, "roles": payload.roles, "updated": True}


@router.get("/roles")
async def list_roles(_: UserContext = Depends(require_permission(Permission.ADMIN_USERS_READ))) -> list[dict]:
    return [
        {"role": "employee", "permissions": [Permission.CORE_RECORDS_READ]},
        {"role": "auditor", "permissions": [Permission.AUDIT_EVENTS_READ]},
        {"role": "admin", "permissions": [permission.value for permission in Permission]},
    ]


@router.put("/roles/{role_id}/permissions")
async def assign_role_permissions(
    role_id: str,
    payload: PermissionAssignRequest,
    _: UserContext = Depends(require_permission(Permission.ADMIN_ROLES_WRITE)),
) -> dict[str, object]:
    return {
        "role_id": role_id,
        "permissions": payload.permissions,
        "updated": True,
    }
