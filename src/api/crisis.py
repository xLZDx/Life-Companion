"""
Crisis support endpoints. ALWAYS PUBLIC - never paywalled, never authenticated.

This enforces GUARDRAILS.md section 6: crisis flow works on free tier, expired
subscription, or even no account.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Query

from src.crisis.hotlines import get_hotlines

router = APIRouter(prefix="/api/crisis", tags=["crisis"])


@router.get("/hotlines")
async def hotlines(
    country: str | None = Query(default=None, max_length=2, description="ISO 3166-1 alpha-2"),
) -> dict[str, Any]:
    """Return geo-mapped crisis hotline list. Public, no auth required."""
    entries = get_hotlines(country)
    return {
        "country": country.upper() if country else None,
        "fallback": country is None or len(entries) > 3,  # signals union-fallback
        "entries": [asdict(e) for e in entries],
    }
