"""Health-pillar endpoints - Phase 4 stubs."""

from __future__ import annotations

from fastapi import APIRouter

from src.auth.deps import CurrentUser

router = APIRouter(prefix="/api/health-pillar", tags=["health-pillar"])


@router.post("/doc")
async def doc_translate_stub(user: CurrentUser) -> dict[str, object]:
    return {
        "user_id": user.uid,
        "translated": None,
        "message": "medical document interpreter wired in Phase 4",
    }


@router.post("/visit/prep")
async def visit_prep_stub(user: CurrentUser) -> dict[str, object]:
    return {
        "user_id": user.uid,
        "questions": [],
        "message": "visit prep wired in Phase 4",
    }
