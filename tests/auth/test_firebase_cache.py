"""
Regression tests for the Redis cache-hit path in `verify_token`.

Covers Python-reviewer H-8: previously the cache hit was `pragma: no cover`
production logic. These tests now exercise the deserialization roundtrip.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from src.auth.firebase import FirebaseUser, _token_cache_key, verify_token


def _key(token: str) -> str:
    expected = f"auth:token:{hashlib.sha256(token.encode('utf-8')).hexdigest()}"
    assert _token_cache_key(token) == expected
    return expected


@pytest.mark.asyncio
async def test_cache_hit_returns_user_without_firebase_call(
    mock_redis: Any,
) -> None:
    """Cache hit must skip the Firebase network call entirely."""
    token = "test-token-cache-hit"
    cached_user = FirebaseUser(
        uid="cached-uid",
        email="cached@example.com",
        email_verified=True,
        custom_claims={"role": "user"},
    )
    await mock_redis.set(
        _key(token),
        json.dumps(
            {
                "uid": cached_user.uid,
                "email": cached_user.email,
                "email_verified": cached_user.email_verified,
                "custom_claims": cached_user.custom_claims,
            }
        ),
    )

    result = await verify_token(token, redis=mock_redis)

    assert result.uid == "cached-uid"
    assert result.email == "cached@example.com"
    assert result.email_verified is True
    assert result.custom_claims == {"role": "user"}


@pytest.mark.asyncio
async def test_cache_key_is_sha256_not_raw_token(mock_redis: Any) -> None:
    """Raw token must never appear in the Redis key (security)."""
    token = "test-token-key-check"
    key = _token_cache_key(token)
    assert token not in key
    assert key.startswith("auth:token:")
    # SHA-256 hex digest = 64 chars
    assert len(key) == len("auth:token:") + 64
