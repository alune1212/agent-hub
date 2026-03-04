from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_me() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["user_id"] == "u_admin"
