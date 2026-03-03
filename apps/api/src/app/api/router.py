from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, audit, auth, core, reports

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(audit.router)
api_router.include_router(reports.router)
api_router.include_router(core.router)
