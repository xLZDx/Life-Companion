"""
LLM provider registry: routes `LLMPurpose` -> concrete adapter.

DEFAULT  -> Gemini (reflection, patterns, health translation)
CRISIS   -> Claude  (best safety calibration)
CLASSIFY -> OpenAI  (cheap intent classification)
"""

from __future__ import annotations

from functools import lru_cache

from src.llm.adapter import LLMAdapter, LLMPurpose
from src.llm.claude_adapter import ClaudeAdapter
from src.llm.gemini import GeminiAdapter
from src.llm.openai_adapter import OpenAIAdapter


@lru_cache(maxsize=3)
def _build(purpose: LLMPurpose) -> LLMAdapter:
    if purpose is LLMPurpose.DEFAULT:
        return GeminiAdapter()
    if purpose is LLMPurpose.CRISIS:
        return ClaudeAdapter()
    if purpose is LLMPurpose.CLASSIFY:
        return OpenAIAdapter()
    raise ValueError(f"Unknown LLMPurpose: {purpose!r}")


def get_llm(purpose: LLMPurpose = LLMPurpose.DEFAULT) -> LLMAdapter:
    """Return the cached adapter for a purpose."""
    return _build(purpose)


def reset_registry_for_tests() -> None:
    """Clear cache so tests can swap adapters via dependency overrides."""
    _build.cache_clear()
