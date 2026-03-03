from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.core.security import UserContext, require_permission
from app.domain.schemas import ReportResult
from py_domain.permissions import Permission

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
async def dashboard(
    _: UserContext = Depends(require_permission(Permission.REPORTS_DASHBOARD_READ)),
) -> dict[str, object]:
    return {
        "active_users": 326,
        "critical_actions_today": 1204,
        "pending_audit_alerts": 7,
    }


@router.get("/{report_code}", response_model=ReportResult)
async def get_report(
    report_code: str,
    _: UserContext = Depends(require_permission(Permission.REPORTS_DASHBOARD_READ)),
) -> ReportResult:
    return ReportResult(
        report_code=report_code,
        generated_at=datetime.utcnow(),
        rows=[
            {"dimension": "dept_a", "value": 123},
            {"dimension": "dept_b", "value": 87},
        ],
    )


@router.post("/{report_code}/export")
async def export_report(
    report_code: str,
    _: UserContext = Depends(require_permission(Permission.REPORTS_DASHBOARD_READ)),
) -> dict[str, str]:
    return {
        "report_code": report_code,
        "task_id": f"task_export_{report_code}",
        "status": "queued",
    }
