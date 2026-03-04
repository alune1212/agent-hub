"""initial schemas and tables

Revision ID: 20260303_0001
Revises:
Create Date: 2026-03-03
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260303_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS app")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")
    op.execute("CREATE SCHEMA IF NOT EXISTS reporting")

    op.create_table(
        "business_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("owner_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )

    op.create_table(
        "outbox_events",
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("event_id"),
        schema="audit",
    )

    op.create_table(
        "audit_log",
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("actor_name", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=False),
        sa.Column("before_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("result", sa.String(length=32), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
        schema="audit",
    )

    op.create_table(
        "fact_user_activity_daily",
        sa.Column("dt", sa.Date(), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("action_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("dt", "actor_id"),
        schema="reporting",
    )


def downgrade() -> None:
    op.drop_table("fact_user_activity_daily", schema="reporting")
    op.drop_table("audit_log", schema="audit")
    op.drop_table("outbox_events", schema="audit")
    op.drop_table("business_records", schema="app")
