"""
FastAPI app entrypoint.

Wires:
- Structured logging (JSON in prod, JSON-to-file + console in dev)
- Auth middleware (Firebase token verification with Redis cache)
- CORS for mobile + dev web
- Routers from src/api/*
- Startup/shutdown lifespan hooks (Redis client, Firebase init)
"""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin.auth import (
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
)
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.api import billing as billing_api
from src.api import crisis as crisis_api
from src.api import health as health_api
from src.api import health_pillar as health_pillar_api
from src.api import patterns as patterns_api
from src.api import reflection as reflection_api
from src.auth.firebase import FirebaseUser
import src.auth.firebase as fb_mod
from src.config import Settings, get_settings

# Routes always reachable without auth.
_ALWAYS_PUBLIC: frozenset[str] = frozenset(
    {
        "/api/health",
        "/api/version",
        "/api/crisis/hotlines",
    }
)
# OpenAPI surface - public in dev, hidden in production (security-reviewer H-3).
_DEV_ONLY_PUBLIC: frozenset[str] = frozenset({"/docs", "/redoc", "/openapi.json"})


def _build_public_paths(settings: Settings) -> frozenset[str]:
    if settings.is_production:
        return _ALWAYS_PUBLIC
    return _ALWAYS_PUBLIC | _DEV_ONLY_PUBLIC


def configure_logging() -> None:
    """structlog setup: JSON in prod, console-readable in dev + test."""
    settings = get_settings()
    level = getattr(logging, settings.log_level)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.is_production:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        # Console in dev + test - JSON during pytest captured output is unreadable.
        renderer = structlog.dev.ConsoleRenderer(colors=not settings.is_test)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stdout,
    )


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Extracts `Authorization: Bearer <token>`, verifies via Firebase (with Redis
    cache), attaches the resulting `FirebaseUser` to `request.state.user`.

    Does NOT 401 here - that decision belongs to per-route dependencies so
    public routes can choose to accept anonymous requests.

    Distinguishes between bad-token errors (user stays None -> 401) and
    Firebase service errors (sets request.state.auth_error -> 503).
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request.state.user = None
        request.state.auth_error = None

        settings = get_settings()
        if request.url.path in _build_public_paths(settings):
            return await call_next(request)

        # Read live Redis client from app state (set by lifespan).
        redis: Redis | None = getattr(request.app.state, "redis", None)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :].strip()
            try:
                user: FirebaseUser = await fb_mod.verify_token(token, redis=redis)
                request.state.user = user
            except (
                ExpiredIdTokenError,
                InvalidIdTokenError,
                RevokedIdTokenError,
                ValueError,
            ):
                # Known bad-token errors: leave user=None; deps will 401.
                pass
            except Exception:
                # Firebase or network outage - tell deps to return 503.
                request.state.auth_error = "service_unavailable"

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    redis: Redis | None = None
    try:
        redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await redis.ping()
        app.state.redis = redis
    except Exception:
        # Degrade gracefully: auth still works (just no cache); fails open on Redis only.
        app.state.redis = None
    yield
    if redis is not None:
        try:
            await redis.aclose()
        except Exception:  # pragma: no cover
            pass


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    # Hide OpenAPI docs in production (security-reviewer H-3).
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"
    openapi_url = None if settings.is_production else "/openapi.json"

    app = FastAPI(
        title="Life Companion API",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    # CORS - Phase 1 surface is GET + POST + OPTIONS only.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Auth middleware reads request.app.state.redis lazily on each request.
    app.add_middleware(AuthMiddleware)

    # Routers
    app.include_router(health_api.router)
    app.include_router(crisis_api.router)
    app.include_router(reflection_api.router)
    app.include_router(patterns_api.router)
    app.include_router(health_pillar_api.router)
    app.include_router(billing_api.router)

    return app


app = create_app()
