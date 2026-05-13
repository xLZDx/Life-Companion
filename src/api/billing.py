"""Billing endpoints - Phase 5 stubs."""

from __future__ import annotations

from fastapi import APIRouter

from src.auth.deps import CurrentUser
from src.billing.tiers import get_tier

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/tier")
async def current_tier(user: CurrentUser) -> dict[str, str]:
    # Phase 5 reads from subscriptions table; Phase 1 defaults to free for everyone.
    tier = get_tier("free")
    return {"user_id": user.uid, "tier": tier.value}
