from __future__ import annotations

from py_domain.events import OutboxEventPayload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OutboxEvent


async def append_outbox_event(
    session: AsyncSession,
    payload: OutboxEventPayload,
    trace_id: str,
) -> OutboxEvent:
    event = OutboxEvent(
        event_type=payload.event_type,
        aggregate_type=payload.aggregate_type,
        aggregate_id=payload.aggregate_id,
        payload=payload.model_dump(mode="json"),
        trace_id=trace_id,
    )
    session.add(event)
    await session.flush()
    return event
