"""Reflection endpoints - Phase 1 stubs. Phase 2 wires the Socratic engine."""

from __future__ import annotations

from fastapi import APIRouter

from src.auth.deps import CurrentUser

router = APIRouter(prefix="/api/reflect", tags=["reflection"])


@router.post("")
async def reflect_stub(user: CurrentUser) -> dict[str, object]:
    """
    Phase 1 stub. Phase 2 wires:
    - crisis detection on input
    - Socratic prompt via Gemini
    - safety filter on output
    - persist to reflections table
    """
    return {
        "crisis": False,
        "ai_response": None,
        "message": "reflection engine wired in Phase 2",
        "user_id": user.uid,
    }
