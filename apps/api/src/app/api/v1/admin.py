from __future__ import annotations

from fastapi import APIRouter, Depends
from py_common import build_trace_id
from py_domain.events import OutboxEventPayload
from py_domain.permissions import Permission
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import UserContext, require_permission
from app.db.models import PermissionEntity, Role, RolePermission
from app.domain.schemas import PermissionAssignRequest, RoleAssignRequest
from app.services.iam import set_user_roles, upsert_user
from app.services.outbox import append_outbox_event

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    _: UserContext = Depends(require_permission(Permission.ADMIN_USERS_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    rows = await session.execute(
        text(
            """
            SELECT
              u.user_id,
              u.user_name,
              COALESCE(
                array_agg(ur.role_id ORDER BY ur.role_id)
                FILTER (WHERE ur.role_id IS NOT NULL),
                ARRAY[]::text[]
              ) AS roles
            FROM app.users u
            LEFT JOIN app.user_roles ur ON ur.user_id = u.user_id
            GROUP BY u.user_id, u.user_name
            ORDER BY u.user_id
            """
        )
    )
    return [
        {
            "user_id": row.user_id,
            "name": row.user_name,
            "roles": list(row.roles),
        }
        for row in rows.mappings().all()
    ]


@router.put("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: str,
    payload: RoleAssignRequest,
    operator: UserContext = Depends(require_permission(Permission.ADMIN_USERS_WRITE)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    trace_id = build_trace_id()
    target_roles = sorted(set(payload.roles))

    try:
        await upsert_user(session, user_id=user_id, user_name=user_id)
        await set_user_roles(session, user_id=user_id, roles=target_roles)

        audit_payload = OutboxEventPayload(
            event_type="admin.user.roles.assigned",
            aggregate_type="user",
            aggregate_id=user_id,
            actor_id=operator.user_id,
            actor_name=operator.user_name,
            action="admin.users.assign_roles",
            detail={"roles": target_roles},
        )
        await append_outbox_event(session, payload=audit_payload, trace_id=trace_id)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return {"user_id": user_id, "roles": target_roles, "updated": True}


@router.get("/roles")
async def list_roles(
    _: UserContext = Depends(require_permission(Permission.ADMIN_USERS_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    rows = await session.execute(
        text(
            """
            SELECT
              r.role_id,
              r.role_name,
              COALESCE(
                array_agg(rp.permission_key ORDER BY rp.permission_key)
                FILTER (WHERE rp.permission_key IS NOT NULL),
                ARRAY[]::text[]
              ) AS permissions
            FROM app.roles r
            LEFT JOIN app.role_permissions rp ON rp.role_id = r.role_id
            GROUP BY r.role_id, r.role_name
            ORDER BY r.role_id
            """
        )
    )
    return [
        {
            "role": row.role_id,
            "role_name": row.role_name,
            "permissions": list(row.permissions),
        }
        for row in rows.mappings().all()
    ]


@router.put("/roles/{role_id}/permissions")
async def assign_role_permissions(
    role_id: str,
    payload: PermissionAssignRequest,
    operator: UserContext = Depends(require_permission(Permission.ADMIN_ROLES_WRITE)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    trace_id = build_trace_id()
    target_permissions = sorted(set(payload.permissions))

    try:
        role = await session.get(Role, role_id)
        if role is None:
            role = Role(role_id=role_id, role_name=role_id.replace("_", " ").title())
            session.add(role)

        existing_permissions = await session.execute(
            select(PermissionEntity.permission_key).where(PermissionEntity.permission_key.in_(target_permissions))
        )
        existing_permission_keys = {row[0] for row in existing_permissions.all()}

        for key in target_permissions:
            if key not in existing_permission_keys:
                session.add(PermissionEntity(permission_key=key, description=key))

        await session.flush()
        await session.execute(delete(RolePermission).where(RolePermission.role_id == role_id))

        for key in target_permissions:
            session.add(RolePermission(role_id=role_id, permission_key=key))

        audit_payload = OutboxEventPayload(
            event_type="admin.role.permissions.assigned",
            aggregate_type="role",
            aggregate_id=role_id,
            actor_id=operator.user_id,
            actor_name=operator.user_name,
            action="admin.roles.assign_permissions",
            detail={"permissions": target_permissions},
        )
        await append_outbox_event(session, payload=audit_payload, trace_id=trace_id)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return {
        "role_id": role_id,
        "permissions": target_permissions,
        "updated": True,
    }
