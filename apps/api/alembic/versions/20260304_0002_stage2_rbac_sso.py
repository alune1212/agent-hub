"""add stage2 rbac and sso tables

Revision ID: 20260304_0002
Revises: 20260303_0001
Create Date: 2026-03-04
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260304_0002"
down_revision = "20260303_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("user_id"),
        schema="app",
    )

    op.create_table(
        "roles",
        sa.Column("role_id", sa.String(length=64), nullable=False),
        sa.Column("role_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("role_id"),
        schema="app",
    )

    op.create_table(
        "permissions",
        sa.Column("permission_key", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("permission_key"),
        schema="app",
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("role_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["role_id"], ["app.roles.role_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["app.users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        schema="app",
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.String(length=64), nullable=False),
        sa.Column("permission_key", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["permission_key"], ["app.permissions.permission_key"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["app.roles.role_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_key"),
        schema="app",
    )

    op.create_table(
        "sso_states",
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("redirect_uri", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("state"),
        schema="app",
    )

    op.execute(
        """
        INSERT INTO app.roles (role_id, role_name)
        VALUES
          ('employee', 'Employee'),
          ('auditor', 'Auditor'),
          ('admin', 'Administrator')
        ON CONFLICT (role_id) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO app.permissions (permission_key, description)
        VALUES
          ('core:records:read', 'Read core records'),
          ('core:records:create', 'Create core records'),
          ('audit:events:read', 'Read audit events'),
          ('reports:dashboard:read', 'Read dashboard and reports'),
          ('admin:users:read', 'Read users'),
          ('admin:users:write', 'Assign user roles'),
          ('admin:roles:write', 'Assign role permissions')
        ON CONFLICT (permission_key) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO app.role_permissions (role_id, permission_key)
        VALUES
          ('employee', 'core:records:read'),
          ('employee', 'core:records:create'),
          ('auditor', 'core:records:read'),
          ('auditor', 'audit:events:read'),
          ('auditor', 'reports:dashboard:read'),
          ('admin', 'core:records:read'),
          ('admin', 'core:records:create'),
          ('admin', 'audit:events:read'),
          ('admin', 'reports:dashboard:read'),
          ('admin', 'admin:users:read'),
          ('admin', 'admin:users:write'),
          ('admin', 'admin:roles:write')
        ON CONFLICT (role_id, permission_key) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO app.users (user_id, user_name, email, is_active)
        VALUES ('u_admin', 'System Admin', 'admin@internal.local', true)
        ON CONFLICT (user_id) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO app.user_roles (user_id, role_id)
        VALUES ('u_admin', 'admin')
        ON CONFLICT (user_id, role_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("sso_states", schema="app")
    op.drop_table("role_permissions", schema="app")
    op.drop_table("user_roles", schema="app")
    op.drop_table("permissions", schema="app")
    op.drop_table("roles", schema="app")
    op.drop_table("users", schema="app")
