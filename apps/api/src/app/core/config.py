from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="INTERNAL_", extra="ignore")

    app_name: str = "Internal Platform API"
    app_env: str = "dev"
    app_version: str = "0.1.0"

    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/internal_platform"
    redis_url: str = "redis://localhost:6379/0"
    auth_allow_debug_headers: bool = True

    sso_mode: str = "mock"
    sso_client_id: str = "internal-platform"
    sso_client_secret: str = "change-me"
    sso_issuer_url: str = "https://sso.example.com"
    sso_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    sso_mock_default_user: str = "u_admin"

    jwt_secret: str = "change-this-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480
    cors_allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
