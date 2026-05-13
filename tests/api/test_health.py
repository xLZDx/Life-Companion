"""Health-check + version endpoint tests. Public, no auth required."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body


def test_version_endpoint_returns_app_version(client: TestClient) -> None:
    response = client.get("/api/version")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "0.1.0"
    assert body["env"] == "test"


def test_health_does_not_require_auth(client: TestClient) -> None:
    # No Authorization header
    response = client.get("/api/health")
    assert response.status_code == 200
