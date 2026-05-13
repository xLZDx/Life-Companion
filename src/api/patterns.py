"""Pattern + weekly-review endpoints - Phase 3 stubs."""

from __future__ import annotations

from fastapi import APIRouter

from src.auth.deps import CurrentUser

router = APIRouter(prefix="/api", tags=["patterns"])


@router.get("/patterns")
async def patterns_stub(user: CurrentUser) -> dict[str, object]:
    return {
        "user_id": user.uid,
        "patterns": [],
        "message": "pattern surfacing wired in Phase 3",
    }


@router.get("/weekly")
async def weekly_stub(user: CurrentUser) -> dict[str, object]:
    return {
        "user_id": user.uid,
        "areas": {},
        "message": "weekly review wired in Phase 3",
    }
