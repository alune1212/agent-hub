from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from py_common import build_trace_id
from py_domain.events import OutboxEventPayload
from py_domain.permissions import Permission
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import UserContext, require_permission
from app.domain.schemas import ReportResult
from app.services.outbox import append_outbox_event

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
async def dashboard(
    _: UserContext = Depends(require_permission(Permission.REPORTS_DASHBOARD_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    active_users = await session.scalar(
        text(
            """
            SELECT COUNT(DISTINCT actor_id)
            FROM audit.audit_log
            WHERE occurred_at >= NOW() - INTERVAL '7 day'
            """
        )
    )
    critical_actions_today = await session.scalar(
        text(
            """
            SELECT COUNT(*)
            FROM audit.audit_log
            WHERE occurred_at::date = CURRENT_DATE
            """
        )
    )
    pending_audit_alerts = await session.scalar(
        text(
            """
            SELECT COUNT(*)
            FROM audit.outbox_events
            WHERE processed_at IS NULL
            """
        )
    )

    return {
        "active_users": int(active_users or 0),
        "critical_actions_today": int(critical_actions_today or 0),
        "pending_audit_alerts": int(pending_audit_alerts or 0),
    }


@router.get("/{report_code}", response_model=ReportResult)
async def get_report(
    report_code: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    _: UserContext = Depends(require_permission(Permission.REPORTS_DASHBOARD_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> ReportResult:
    if start_date is None:
        start_date = date.today() - timedelta(days=7)
    if end_date is None:
        end_date = date.today()

    if report_code == "user_activity_daily":
        rows = await session.execute(
            text(
                """
                SELECT dt, actor_id, action_count
                FROM reporting.fact_user_activity_daily
                WHERE dt BETWEEN :start_date AND :end_date
                ORDER BY dt DESC, actor_id ASC
                LIMIT :limit
                """
            ),
            {
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
        )
        data = [
            {
                "dt": row.dt,
                "actor_id": row.actor_id,
                "action_count": row.action_count,
            }
            for row in rows.mappings().all()
        ]
    elif report_code == "audit_action_top":
        rows = await session.execute(
            text(
                """
                SELECT action, COUNT(*) AS count
                FROM audit.audit_log
                WHERE occurred_at::date BETWEEN :start_date AND :end_date
                GROUP BY action
                ORDER BY count DESC, action ASC
                LIMIT :limit
                """
            ),
            {
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
        )
        data = [{"action": row.action, "count": row.count} for row in rows.mappings().all()]
    else:
        raise HTTPException(status_code=404, detail=f"Unsupported report code: {report_code}")

    return ReportResult(
        report_code=report_code,
        generated_at=datetime.now(tz=UTC),
        rows=data,
    )


@router.post("/{report_code}/export")
async def export_report(
    report_code: str,
    operator: UserContext = Depends(require_permission(Permission.REPORTS_DASHBOARD_READ)),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    trace_id = build_trace_id()
    task_id = f"report_export_{trace_id[:12]}"

    try:
        payload = OutboxEventPayload(
            event_type="report.export.requested",
            aggregate_type="report_export",
            aggregate_id=task_id,
            actor_id=operator.user_id,
            actor_name=operator.user_name,
            action="reports.export",
            detail={"task_id": task_id, "report_code": report_code},
        )
        await append_outbox_event(session, payload=payload, trace_id=trace_id)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return {
        "report_code": report_code,
        "task_id": task_id,
        "status": "queued",
    }
