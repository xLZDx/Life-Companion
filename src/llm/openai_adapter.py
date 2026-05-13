"""
OpenAI adapter (CLASSIFY purpose - cheap o-mini for intent classification).

Phase 1 stub. Phase 2+ wires openai SDK with gpt-4o-mini.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from src.config import get_settings
from src.llm.adapter import LLMAdapter, LLMMessage, LLMResponse


class OpenAIAdapter(LLMAdapter):
    @property
    def provider_name(self) -> str:
        return "openai"

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
        request_id: str | None = None,
    ) -> LLMResponse:
        raise NotImplementedError("Phase 2 implements OpenAI complete()")

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        request_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError("Phase 2 implements OpenAI stream()")
        yield ""  # pragma: no cover

    async def classify(
        self,
        text: str,
        labels: list[str],
        *,
        request_id: str | None = None,
    ) -> str:
        raise NotImplementedError("Phase 2 implements OpenAI classify()")

    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        # gpt-4o-mini pricing snapshot.
        return (tokens_in * 0.15e-6) + (tokens_out * 0.60e-6)
