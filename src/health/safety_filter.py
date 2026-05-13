"""
No-diagnosis safety filter.

Phase 1: passthrough stub returning (True, None).
Phase 4: regex + LLM check enforcing GUARDRAILS.md section 2.

The filter inspects AI-generated text BEFORE it reaches the user. On hit, the
caller regenerates once; if the regeneration still hits, the caller returns a
safe canned response ("I'd rather not say that - please see a doctor for
diagnosis").

Phase 4 will populate `BANNED_PHRASES` (EN + RU) and add an LLM second-pass
check using OpenAI o-mini for fuzzy diagnostic-language detection.
"""

from __future__ import annotations

# Phase 4 will populate. Each tuple: (regex_pattern, reason_code).
BANNED_PHRASES: list[tuple[str, str]] = []


def check_output(text: str) -> tuple[bool, str | None]:
    """
    Return (is_safe, reason_code).

    Phase 1: always returns (True, None) - passthrough.
    Phase 4: regex check against BANNED_PHRASES + LLM second-pass.

    Args:
        text: AI-generated text candidate for delivery to user.

    Returns:
        (True, None) if safe to send.
        (False, reason_code) if diagnostic language detected - caller
        regenerates once before falling back to a safe canned response.
    """
    if not text:
        return True, None
    return True, None
