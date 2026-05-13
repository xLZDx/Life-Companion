"""LLM adapter interface + cost-tracking + log-content invariants."""

from __future__ import annotations

import pytest

from src.llm.adapter import (
    CostTracker,
    LLMAdapter,
    LLMCallLog,
    LLMMessage,
    LLMPurpose,
    LLMResponse,
)
from src.llm.registry import get_llm, reset_registry_for_tests


def test_cost_tracker_accumulates() -> None:
    tracker = CostTracker()
    tracker.record(0.05)
    tracker.record(0.10)
    assert tracker.total_usd == pytest.approx(0.15)
    assert tracker.call_count == 2


def test_call_log_hash_user_id_is_deterministic() -> None:
    h1 = LLMCallLog.hash_user_id("user-123")
    h2 = LLMCallLog.hash_user_id("user-123")
    h3 = LLMCallLog.hash_user_id("user-456")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64  # SHA-256 hex


def test_call_log_has_no_content_fields() -> None:
    """Critical invariant: LLMCallLog must NEVER carry message content."""
    log = LLMCallLog(
        request_id="r1",
        user_id_hash="h",
        provider="gemini",
        model="gemini-3.1-pro-preview",
        purpose=LLMPurpose.DEFAULT,
        tokens_in=10,
        tokens_out=20,
        cost_usd=0.001,
        latency_ms=300,
        success=True,
    )
    fields = vars(log).keys()
    forbidden = {"content", "user_message", "ai_response", "messages", "text"}
    assert not (fields & forbidden), f"Forbidden content fields present: {fields & forbidden}"


def test_registry_routes_purposes_to_distinct_providers() -> None:
    reset_registry_for_tests()
    default_llm = get_llm(LLMPurpose.DEFAULT)
    crisis_llm = get_llm(LLMPurpose.CRISIS)
    classify_llm = get_llm(LLMPurpose.CLASSIFY)
    assert default_llm.provider_name == "gemini"
    assert crisis_llm.provider_name == "claude"
    assert classify_llm.provider_name == "openai"


def test_registry_caches_instances() -> None:
    reset_registry_for_tests()
    a = get_llm(LLMPurpose.DEFAULT)
    b = get_llm(LLMPurpose.DEFAULT)
    assert a is b


def test_estimate_cost_returns_nonnegative() -> None:
    for purpose in LLMPurpose:
        llm = get_llm(purpose)
        cost = llm.estimate_cost(100, 50)
        assert cost >= 0
        assert isinstance(cost, float)


def test_llm_response_is_dataclass() -> None:
    resp = LLMResponse(
        content="hello",
        provider="gemini",
        model="x",
        tokens_in=1,
        tokens_out=2,
        cost_usd=0.0,
        latency_ms=10,
    )
    assert resp.content == "hello"
    assert resp.structured is None


def test_llm_message_is_dataclass() -> None:
    msg = LLMMessage(role="user", content="hi")
    assert msg.role == "user"


def test_llm_adapter_is_abstract() -> None:
    with pytest.raises(TypeError):
        LLMAdapter()  # type: ignore[abstract]
