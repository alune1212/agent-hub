from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.core.security import UserContext, require_permission
from py_domain.permissions import Permission

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
async def list_events(
    _: UserContext = Depends(require_permission(Permission.AUDIT_EVENTS_READ)),
) -> list[dict]:
    return [
        {
            "event_id": "evt_001",
            "actor_id": "u_admin",
            "action": "admin.users.update_role",
            "resource_type": "user",
            "resource_id": "u_auditor",
            "result": "success",
            "trace_id": "trace_evt_001",
            "occurred_at": datetime.utcnow(),
        }
    ]


@router.get("/events/{event_id}")
async def get_event(
    event_id: str,
    _: UserContext = Depends(require_permission(Permission.AUDIT_EVENTS_READ)),
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "actor_id": "u_admin",
        "action": "admin.users.update_role",
        "resource_type": "user",
        "resource_id": "u_auditor",
        "result": "success",
    }


@router.post("/export")
async def export_events(
    _: UserContext = Depends(require_permission(Permission.AUDIT_EVENTS_READ)),
) -> dict[str, str]:
    return {
        "task_id": "task_export_audit_001",
        "status": "queued",
    }
