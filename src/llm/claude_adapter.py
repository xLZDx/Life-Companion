"""
Claude adapter (CRISIS purpose - best safety calibration).

Phase 1 stub. Phase 2 wires anthropic SDK with Sonnet 4.6.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from src.config import get_settings
from src.llm.adapter import LLMAdapter, LLMMessage, LLMResponse


class ClaudeAdapter(LLMAdapter):
    @property
    def provider_name(self) -> str:
        return "claude"

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.anthropic_api_key
        self.model = settings.claude_model

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
        request_id: str | None = None,
    ) -> LLMResponse:
        raise NotImplementedError("Phase 2 implements Claude complete()")

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        request_id: str | None = None,
    ) -> AsyncIterator[str]:
        raise NotImplementedError("Phase 2 implements Claude stream()")

    async def classify(
        self,
        text: str,
        labels: list[str],
        *,
        request_id: str | None = None,
    ) -> str:
        raise NotImplementedError("Phase 2 implements Claude classify()")

    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        # Claude Sonnet 4.6 pricing snapshot; refine in Phase 2.
        return (tokens_in * 3.0e-6) + (tokens_out * 15.0e-6)
