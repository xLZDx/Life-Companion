"""Auth dependency tests via TestClient end-to-end."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_protected_route_returns_401_without_token(client: TestClient) -> None:
    response = client.post("/api/reflect")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_protected_route_returns_401_with_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/reflect",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401


def test_protected_route_succeeds_with_valid_token(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/api/reflect", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["crisis"] is False
    assert body["user_id"] == "test-uid-123"


def test_public_crisis_hotlines_does_not_require_token(client: TestClient) -> None:
    response = client.get("/api/crisis/hotlines?country=RU")
    assert response.status_code == 200
