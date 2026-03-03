from worker.config import to_sync_database_url


def test_to_sync_database_url() -> None:
    url = "postgresql+asyncpg://postgres:postgres@localhost:5432/internal_platform"
    assert to_sync_database_url(url) == "postgresql+psycopg://postgres:postgres@localhost:5432/internal_platform"
