"""
Firebase ID-token verification with Redis cache.

The middleware in main.py extracts the Bearer token, calls `verify_token`, and
attaches the resulting `FirebaseUser` to `request.state.user`. Routes that need
auth pull it via `Depends(get_current_user)` from `deps.py`.

Redis cache key: `auth:token:<sha256(token)>`
TTL: settings.redis_token_ttl_seconds (default 900s, shorter than Firebase's
1-hour token lifetime so we tolerate clock skew without serving stale tokens).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from redis.asyncio import Redis

from src.config import get_settings

log = logging.getLogger(__name__)

_firebase_initialized = False


@dataclass(frozen=True)
class FirebaseUser:
    """Verified Firebase user, attached to request.state.user."""

    uid: str
    email: str | None = None
    email_verified: bool = False
    custom_claims: dict[str, Any] = field(default_factory=dict)


def _initialize_firebase() -> None:
    """Initialize firebase_admin once per process."""
    global _firebase_initialized
    if _firebase_initialized:
        return
    settings = get_settings()
    if settings.firebase_service_account_path:
        cred = credentials.Certificate(settings.firebase_service_account_path)
        firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
    else:
        # Application Default Credentials (gcloud auth) or test mode
        try:
            firebase_admin.initialize_app(
                options={"projectId": settings.firebase_project_id}
            )
        except ValueError:
            # Already initialized (e.g. test fixture); fine.
            pass
    _firebase_initialized = True


def _token_cache_key(token: str) -> str:
    return f"auth:token:{hashlib.sha256(token.encode('utf-8')).hexdigest()}"


async def verify_token(token: str, redis: Redis | None = None) -> FirebaseUser:
    """
    Verify a Firebase ID token. Cached in Redis for `redis_token_ttl_seconds`.

    Raises:
        firebase_admin.auth.InvalidIdTokenError - bad signature / format
        firebase_admin.auth.ExpiredIdTokenError - token expired
        firebase_admin.auth.RevokedIdTokenError - token revoked by Firebase
        ValueError - malformed token (empty string, etc.)
    """
    if not token:
        raise ValueError("Empty token")

    cache_key = _token_cache_key(token)

    # ---- Cache hit ----
    if redis is not None:
        try:
            cached = await redis.get(cache_key)
            if cached is not None:
                payload = json.loads(cached)
                return FirebaseUser(**payload)
        except Exception as exc:  # pragma: no cover - Redis outage path
            log.warning("auth.cache_miss_due_to_redis_error", exc_info=exc)

    # ---- Cache miss: call Firebase ----
    _initialize_firebase()
    decoded = firebase_auth.verify_id_token(token, check_revoked=True)
    user = FirebaseUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        email_verified=bool(decoded.get("email_verified", False)),
        custom_claims=dict(decoded.get("custom_claims", {}) or {}),
    )

    # ---- Cache write ----
    if redis is not None:
        try:
            settings = get_settings()
            await redis.set(
                cache_key,
                json.dumps(asdict(user)),
                ex=settings.redis_token_ttl_seconds,
            )
        except Exception as exc:  # pragma: no cover
            log.warning("auth.cache_write_failed", exc_info=exc)

    return user
