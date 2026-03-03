from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="INTERNAL_")

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/internal_platform"


@lru_cache
def get_settings() -> WorkerSettings:
    return WorkerSettings()


def to_sync_database_url(url: str) -> str:
    return url.replace("+asyncpg", "+psycopg")
