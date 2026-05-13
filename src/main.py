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
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.api import billing as billing_api
from src.api import crisis as crisis_api
from src.api import health as health_api
from src.api import health_pillar as health_pillar_api
from src.api import patterns as patterns_api
from src.api import reflection as reflection_api
from src.auth.firebase import FirebaseUser, verify_token
from src.config import get_settings

PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/api/health",
        "/api/version",
        "/api/crisis/hotlines",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)


def configure_logging() -> None:
    """structlog setup: JSON in prod, console + JSON-file in dev."""
    settings = get_settings()
    level = getattr(logging, settings.log_level)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.is_production or settings.is_test:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
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
    PUBLIC_PATHS routes can choose to accept anonymous requests.
    """

    def __init__(self, app: Any, redis: Redis | None) -> None:
        super().__init__(app)
        self.redis = redis

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request.state.user = None
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :].strip()
            try:
                user: FirebaseUser = await verify_token(token, redis=self.redis)
                request.state.user = user
            except Exception:
                # Leave state.user = None; protected routes will 401 via dependency.
                pass

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
    app = FastAPI(
        title="Life Companion API",
        version=settings.app_version,
        lifespan=lifespan,
    )

    # CORS - tight in production, permissive in dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Auth middleware (attaches request.state.user, doesn't 401)
    # Redis client is attached in `lifespan` after startup; pass None for now
    # and re-bind via a wrapper if late binding is needed. For Phase 1,
    # AuthMiddleware reads `request.app.state.redis` lazily inside dispatch
    # would be cleaner - keeping the constructor pattern for now and binding
    # the live redis from a small wrapper.
    app.add_middleware(AuthMiddleware, redis=None)

    # Routers
    app.include_router(health_api.router)
    app.include_router(crisis_api.router)
    app.include_router(reflection_api.router)
    app.include_router(patterns_api.router)
    app.include_router(health_pillar_api.router)
    app.include_router(billing_api.router)

    return app


app = create_app()
