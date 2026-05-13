"""
Gemini adapter (DEFAULT purpose).

Phase 1: structural stub - methods raise NotImplementedError.
Phase 2: wires google-generativeai with `gemini-3.1-pro-preview` primary +
         `gemini-2.5-flash` fallback, streaming via SSE, JSON mode for
         structured output, tenacity retries.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from src.config import get_settings
from src.llm.adapter import LLMAdapter, LLMMessage, LLMResponse


class GeminiAdapter(LLMAdapter):
    @property
    def provider_name(self) -> str:
        return "gemini"

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.primary_model = settings.gemini_model_primary
        self.fallback_model = settings.gemini_model_fallback

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
        request_id: str | None = None,
    ) -> LLMResponse:
        raise NotImplementedError("Phase 2 implements Gemini complete()")

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        request_id: str | None = None,
    ) -> AsyncIterator[str]:
        raise NotImplementedError("Phase 2 implements Gemini stream()")

    async def classify(
        self,
        text: str,
        labels: list[str],
        *,
        request_id: str | None = None,
    ) -> str:
        raise NotImplementedError("Phase 2 implements Gemini classify()")

    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        # Gemini 2.5 Pro pricing as of late 2026; refine in Phase 2 with provider call.
        return (tokens_in * 1.25e-6) + (tokens_out * 5.0e-6)
