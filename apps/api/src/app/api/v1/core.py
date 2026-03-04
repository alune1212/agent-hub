from __future__ import annotations

from fastapi import APIRouter, Depends
from py_common import build_trace_id
from py_domain.events import OutboxEventPayload
from py_domain.permissions import Permission
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import UserContext, require_permission
from app.db.models import BusinessRecord
from app.domain.schemas import BusinessRecordCreate, BusinessRecordResponse
from app.services.outbox import append_outbox_event

router = APIRouter(prefix="/core", tags=["core"])


@router.post("/records", response_model=BusinessRecordResponse)
async def create_record(
    payload: BusinessRecordCreate,
    session: AsyncSession = Depends(get_db_session),
    user: UserContext = Depends(require_permission(Permission.CORE_RECORDS_CREATE)),
) -> BusinessRecordResponse:
    trace_id = build_trace_id()

    record = BusinessRecord(title=payload.title, owner_id=user.user_id)
    try:
        session.add(record)
        await session.flush()

        outbox_payload = OutboxEventPayload(
            event_type="business.record.created",
            aggregate_type="business_record",
            aggregate_id=record.id,
            actor_id=user.user_id,
            actor_name=user.user_name,
            action="core.records.create",
            detail={"title": payload.title},
        )
        await append_outbox_event(session, payload=outbox_payload, trace_id=trace_id)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return BusinessRecordResponse(id=record.id, title=record.title, owner_id=record.owner_id)
