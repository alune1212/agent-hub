from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(BaseModel):
    user_id: str
    user_name: str
    permissions: list[str]


class BusinessRecordCreate(BaseModel):
    title: str


class BusinessRecordResponse(BaseModel):
    id: str
    title: str
    owner_id: str


class RoleAssignRequest(BaseModel):
    roles: list[str]


class PermissionAssignRequest(BaseModel):
    permissions: list[str]


class ReportResult(BaseModel):
    report_code: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    rows: list[dict]
