"""
Shared test fixtures.

External services are mocked - tests NEVER call real Firebase, real LLMs,
real Redis, or real Postgres. The `db_session` fixture is the exception:
when run with `pytest-postgresql`, it spins up an ephemeral Postgres process
(see `tests/db/test_models.py`). Pure-logic tests do not need it.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ---- Default env so importing src.config doesn't blow up ----
os.environ.setdefault("SECRET_KEY", "test-secret-key-32-chars-minimum-here-padding")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


# Re-import after env is set
from src.auth.firebase import FirebaseUser  # noqa: E402
from src.config import get_settings  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _clear_settings_cache() -> Iterator[None]:
    """Ensure Settings is re-read after conftest env-var setup."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def firebase_user() -> FirebaseUser:
    """Canonical test user attached when `auth_headers` is used."""
    return FirebaseUser(
        uid="test-uid-123",
        email="test@example.com",
        email_verified=True,
        custom_claims={},
    )


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Authorization header recognized by the test-bypass auth middleware."""
    return {"Authorization": "Bearer test-token-valid"}


@pytest.fixture
def app(firebase_user: FirebaseUser) -> Iterator[FastAPI]:
    """
    Build a fresh app with the auth middleware bypassed for tests.

    Strategy: monkey-patch `src.auth.firebase.verify_token` to return the
    canonical test user for any token starting with `test-token-valid`,
    raise InvalidIdTokenError otherwise. This avoids touching real Firebase.
    """
    import src.auth.firebase as fb_mod

    async def fake_verify(token: str, redis: Any = None) -> FirebaseUser:
        if not token or token == "invalid":
            raise ValueError("Bad token")
        if not token.startswith("test-token-valid"):
            from firebase_admin.auth import InvalidIdTokenError

            raise InvalidIdTokenError("Bad token")
        return firebase_user

    original = fb_mod.verify_token
    fb_mod.verify_token = fake_verify  # type: ignore[assignment]
    try:
        from src.main import create_app

        yield create_app()
    finally:
        fb_mod.verify_token = original  # type: ignore[assignment]


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def mock_redis() -> AsyncIterator[Any]:
    """In-process fake Redis (via fakeredis). For tests that need cache behavior."""
    import fakeredis.aioredis as fake

    redis = fake.FakeRedis(decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()
