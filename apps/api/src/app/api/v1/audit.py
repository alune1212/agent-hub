from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from py_common import build_trace_id
from py_domain.events import OutboxEventPayload
from py_domain.permissions import Permission
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import UserContext, require_permission
from app.db.models import AuditLog
from app.services.outbox import append_outbox_event

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
async def list_events(
    actor_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    _: UserContext = Depends(require_permission(Permission.AUDIT_EVENTS_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    conditions = []
    if actor_id:
        conditions.append(AuditLog.actor_id == actor_id)
    if action:
        conditions.append(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        conditions.append(AuditLog.resource_type == resource_type)
    if start_at:
        conditions.append(AuditLog.occurred_at >= start_at)
    if end_at:
        conditions.append(AuditLog.occurred_at <= end_at)

    total = await session.scalar(select(func.count()).select_from(AuditLog).where(*conditions))
    rows = await session.execute(
        select(AuditLog)
        .where(*conditions)
        .order_by(AuditLog.occurred_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    items = [
        {
            "event_id": event.event_id,
            "actor_id": event.actor_id,
            "actor_name": event.actor_name,
            "action": event.action,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "result": event.result,
            "trace_id": event.trace_id,
            "occurred_at": event.occurred_at,
        }
        for event in rows.scalars().all()
    ]

    return {
        "items": items,
        "total": int(total or 0),
        "page": page,
        "page_size": page_size,
    }


@router.get("/events/{event_id}")
async def get_event(
    event_id: str,
    _: UserContext = Depends(require_permission(Permission.AUDIT_EVENTS_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    event = await session.get(AuditLog, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Audit event not found")

    return {
        "event_id": event.event_id,
        "actor_id": event.actor_id,
        "actor_name": event.actor_name,
        "action": event.action,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "before": event.before_data,
        "after": event.after_data,
        "ip": event.ip,
        "user_agent": event.user_agent,
        "result": event.result,
        "trace_id": event.trace_id,
        "occurred_at": event.occurred_at,
    }


@router.post("/export")
async def export_events(
    operator: UserContext = Depends(require_permission(Permission.AUDIT_EVENTS_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    trace_id = build_trace_id()
    task_id = f"audit_export_{trace_id[:12]}"

    try:
        payload = OutboxEventPayload(
            event_type="audit.export.requested",
            aggregate_type="audit_export",
            aggregate_id=task_id,
            actor_id=operator.user_id,
            actor_name=operator.user_name,
            action="audit.events.export",
            detail={"task_id": task_id},
        )
        await append_outbox_event(session, payload=payload, trace_id=trace_id)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return {
        "task_id": task_id,
        "status": "queued",
    }
