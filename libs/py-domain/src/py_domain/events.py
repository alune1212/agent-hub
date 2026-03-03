from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OutboxEventPayload(BaseModel):
    event_type: str
    aggregate_type: str
    aggregate_id: str
    actor_id: str
    actor_name: str
    action: str
    detail: dict[str, Any] = Field(default_factory=dict)


class AuditEvent(BaseModel):
    event_id: str
    actor_id: str
    actor_name: str
    action: str
    resource_type: str
    resource_id: str
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    ip: str | None = None
    user_agent: str | None = None
    result: str
    trace_id: str
    occurred_at: datetime


class ReportQuery(BaseModel):
    report_code: str
    start_date: datetime
    end_date: datetime
    group_by: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    page: int = 1
    page_size: int = 20
