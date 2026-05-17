"""
Async SQLAlchemy engine + session factory + FastAPI dependency.

Uses psycopg3 as the driver. The engine is a process-level singleton lazily
constructed via `get_engine()`. Sessions are per-request via `get_session()`,
which yields an `AsyncSession` and closes it on request teardown.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Construct and cache the async engine for the process lifetime."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        echo=False,
    )


@lru_cache(maxsize=1)
def _session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an `AsyncSession` per request."""
    factory = _session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def reset_engine_for_tests() -> None:
    """Test helper: clear cached engine/session factory between fixtures."""
    get_engine.cache_clear()
    _session_factory.cache_clear()
