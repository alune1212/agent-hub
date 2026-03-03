from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_auth_login() -> None:
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 200
    assert response.json()["provider"] == "oidc"


def test_reports_dashboard() -> None:
    response = client.get("/api/v1/reports/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "active_users" in data
