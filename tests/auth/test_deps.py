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


def test_protected_route_returns_503_when_auth_service_fails(
    client: TestClient,
) -> None:
    """If verify_token raises a non-token-shape error, deps must return 503."""
    import src.auth.firebase as fb_mod
    from src.auth.firebase import FirebaseUser

    async def boom(token: str, redis: object = None) -> FirebaseUser:
        raise RuntimeError("Firebase network unreachable")

    original = fb_mod.verify_token
    fb_mod.verify_token = boom  # type: ignore[assignment]
    try:
        response = client.post(
            "/api/reflect",
            headers={"Authorization": "Bearer test-token-valid"},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "Authentication service unavailable"
    finally:
        fb_mod.verify_token = original  # type: ignore[assignment]
