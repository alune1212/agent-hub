from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import create_engine, text

from py_common import configure_logging
from worker.celery_app import celery_app
from worker.config import get_settings, to_sync_database_url

configure_logging()

_settings = get_settings()
_engine = create_engine(to_sync_database_url(_settings.database_url), pool_pre_ping=True)


@celery_app.task(name="worker.tasks.consume_outbox")
def consume_outbox(batch_size: int = 200) -> dict[str, Any]:
    processed = 0
    with _engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT event_id, aggregate_type, aggregate_id, payload, trace_id
                FROM audit.outbox_events
                WHERE processed_at IS NULL
                ORDER BY created_at ASC
                LIMIT :limit
                """
            ),
            {"limit": batch_size},
        ).mappings().all()

        for row in rows:
            payload = row["payload"]
            actor_id = payload.get("actor_id", "unknown")
            actor_name = payload.get("actor_name", "unknown")
            action = payload.get("action", row["aggregate_type"])

            conn.execute(
                text(
                    """
                    INSERT INTO audit.audit_log (
                      event_id, actor_id, actor_name, action,
                      resource_type, resource_id, before_data, after_data,
                      ip, user_agent, result, trace_id, occurred_at
                    ) VALUES (
                      :event_id, :actor_id, :actor_name, :action,
                      :resource_type, :resource_id, NULL, :after_data,
                      NULL, NULL, 'success', :trace_id, NOW()
                    )
                    ON CONFLICT (event_id) DO NOTHING
                    """
                ),
                {
                    "event_id": row["event_id"],
                    "actor_id": actor_id,
                    "actor_name": actor_name,
                    "action": action,
                    "resource_type": row["aggregate_type"],
                    "resource_id": row["aggregate_id"],
                    "after_data": payload,
                    "trace_id": row["trace_id"],
                },
            )

            conn.execute(
                text(
                    """
                    INSERT INTO reporting.fact_user_activity_daily (dt, actor_id, action_count, updated_at)
                    VALUES (CURRENT_DATE, :actor_id, 1, NOW())
                    ON CONFLICT (dt, actor_id)
                    DO UPDATE SET
                      action_count = reporting.fact_user_activity_daily.action_count + 1,
                      updated_at = NOW()
                    """
                ),
                {"actor_id": actor_id},
            )

            conn.execute(
                text(
                    """
                    UPDATE audit.outbox_events
                    SET processed_at = NOW()
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": row["event_id"]},
            )
            processed += 1

    return {"processed": processed, "checked_at": datetime.now(tz=timezone.utc).isoformat()}


@celery_app.task(name="worker.tasks.daily_reconcile")
def daily_reconcile() -> dict[str, Any]:
    with _engine.begin() as conn:
        total_events = conn.execute(text("SELECT COUNT(*) FROM audit.audit_log")).scalar_one()
        daily_users = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM reporting.fact_user_activity_daily
                WHERE dt = CURRENT_DATE
                """
            )
        ).scalar_one()

    return {
        "total_events": int(total_events),
        "today_actors": int(daily_users),
        "checked_at": datetime.now(tz=timezone.utc).isoformat(),
    }
