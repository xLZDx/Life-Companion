"""
Provider-agnostic LLM adapter interface.

Concrete providers (Gemini, Claude, OpenAI) inherit `LLMAdapter` and implement
the five abstract methods. Phase 1 ships stubs that raise NotImplementedError;
Phase 2 wires the first real implementation (Gemini for reflection, Claude for
crisis classification).

The `LLMCallLog` dataclass is intentionally content-free - we log metadata
(provider, tokens, latency, cost) for debugging but never the user message
or AI response. Content lives only in encrypted DB columns (see db/models.py).
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LLMPurpose(str, Enum):
    """Routing hint passed to `get_llm()` to select a provider."""

    DEFAULT = "default"  # Gemini - reflection, pattern surfacing, health translation
    CRISIS = "crisis"  # Claude - crisis classification (better safety calibration)
    CLASSIFY = "classify"  # OpenAI o-mini - cheap intent classification


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    structured: dict[str, Any] | None = None  # populated if json_mode=True


@dataclass
class LLMCallLog:
    """
    Metadata-only record of an LLM call.

    NEVER contains message content. Used by structlog (Phase 1) and may be
    persisted to a log table (Phase 2+).
    """

    request_id: str
    user_id_hash: str  # SHA-256 of user_id; raw uid is never logged
    provider: str
    model: str
    purpose: LLMPurpose
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    success: bool
    error_type: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def hash_user_id(user_id: str) -> str:
        return hashlib.sha256(user_id.encode("utf-8")).hexdigest()


@dataclass
class CostTracker:
    """Accumulates cost across multiple LLM calls in one request context."""

    total_usd: float = 0.0
    call_count: int = 0

    def record(self, cost_usd: float) -> None:
        self.total_usd += cost_usd
        self.call_count += 1


class LLMAdapter(ABC):
    """Minimal provider-agnostic interface. Phase 2-7 expand as features land."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
        request_id: str | None = None,
    ) -> LLMResponse:
        """Single-shot completion."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        request_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming completion - yields token chunks."""
        ...

    @abstractmethod
    async def classify(
        self,
        text: str,
        labels: list[str],
        *,
        request_id: str | None = None,
    ) -> str:
        """Single-label classification. Returns the chosen label."""
        ...

    @abstractmethod
    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Return estimated USD cost for a call with these token counts."""
        ...
