from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.domain.schemas import HealthResponse
from py_common import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/healthz", response_model=HealthResponse, tags=["health"])
    async def healthz() -> HealthResponse:
        return HealthResponse()

    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    configure_logging()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


def export_openapi(output: str) -> None:
    spec = app.openapi()
    Path(output).write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Internal API utility")
    parser.add_argument("--export-openapi", type=str, default="", help="Export OpenAPI schema path")
    args = parser.parse_args()

    if args.export_openapi:
        export_openapi(args.export_openapi)
    else:
        run()
