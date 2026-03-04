from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "app"}

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "app"}

    role_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PermissionEntity(Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "app"}

    permission_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "app"}

    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app.users.user_id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app.roles.role_id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "app"}

    role_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app.roles.role_id", ondelete="CASCADE"), primary_key=True
    )
    permission_key: Mapped[str] = mapped_column(
        String(100), ForeignKey("app.permissions.permission_key", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BusinessRecord(Base):
    __tablename__ = "business_records"
    __table_args__ = {"schema": "app"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    __table_args__ = {"schema": "audit"}

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit"}

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    before_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FactUserActivityDaily(Base):
    __tablename__ = "fact_user_activity_daily"
    __table_args__ = {"schema": "reporting"}

    dt: Mapped[date] = mapped_column(Date, primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    action_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SSOState(Base):
    __tablename__ = "sso_states"
    __table_args__ = {"schema": "app"}

    state: Mapped[str] = mapped_column(String(64), primary_key=True)
    redirect_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
