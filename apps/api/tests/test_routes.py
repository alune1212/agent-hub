from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_auth_login() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["user_id"] == "u_admin"


def test_reports_dashboard() -> None:
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "logout success"
