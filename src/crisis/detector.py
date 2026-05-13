"""
Crisis detection - Phase 1 stub.

Phase 2 fills in:
- REGEX_TRIGGERS: exhaustive multilingual phrase list (EN + RU + scalable)
- LLM classifier path (Claude Sonnet 4.6) with structured-output category
- OR logic: regex OR llm -> True (never AND)

Returning False from this stub in Phase 1 is correct: no real users yet,
endpoints that would call this are stubs returning placeholder data.
The TEST in tests/crisis/ asserts the contract; Phase 2 parametrizes triggers.
"""

from __future__ import annotations

# Phase 2 will populate this list. Entries are tuples of (pattern, category).
# Categories must match the CrisisEvent.trigger_category enum:
# suicidal_ideation | self_harm | harm_to_others | medical_emergency | abuse
REGEX_TRIGGERS: list[tuple[str, str]] = []


def is_crisis(message: str, lang: str = "auto") -> bool:
    """
    Return True if `message` matches a crisis trigger.

    Phase 1: stub returns False (no real users yet).
    Phase 2: regex check + (optional) LLM classifier check, OR-combined.
    """
    if not message:
        return False
    return False
