"""Health-check + version endpoints. Public (no auth required)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from src.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/version")
async def version() -> dict[str, str]:
    settings = get_settings()
    return {
        "version": settings.app_version,
        "env": settings.app_env,
    }
