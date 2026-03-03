from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    CORE_RECORDS_READ = "core:records:read"
    CORE_RECORDS_CREATE = "core:records:create"
    AUDIT_EVENTS_READ = "audit:events:read"
    REPORTS_DASHBOARD_READ = "reports:dashboard:read"
    ADMIN_USERS_READ = "admin:users:read"
    ADMIN_USERS_WRITE = "admin:users:write"
    ADMIN_ROLES_WRITE = "admin:roles:write"
