"""
Tier-gating tests. The critical invariant: crisis features are NEVER gated.
"""

from __future__ import annotations

import pytest

from src.billing.tiers import ALWAYS_ALLOWED, Tier, check_feature_access, get_tier


# --------------------------- Crisis-always-free invariant --------------------------- #


@pytest.mark.parametrize("tier", list(Tier))
@pytest.mark.parametrize("feature", sorted(ALWAYS_ALLOWED))
def test_always_allowed_features_work_for_every_tier(tier: Tier, feature: str) -> None:
    """GUARDRAILS section 6 - crisis MUST always work, regardless of tier."""
    assert check_feature_access(tier, feature) is True


def test_crisis_hotlines_specifically_in_always_allowed() -> None:
    assert "crisis.hotlines" in ALWAYS_ALLOWED
    assert "crisis.detect" in ALWAYS_ALLOWED


# --------------------------- Standard gating --------------------------- #


def test_free_tier_blocked_from_plus_features() -> None:
    assert check_feature_access(Tier.FREE, "life.checkin.unlimited") is False
    assert check_feature_access(Tier.FREE, "mind.reflection.unlimited") is False
    assert check_feature_access(Tier.FREE, "health.doc.translate") is False


def test_plus_tier_allowed_for_plus_features() -> None:
    assert check_feature_access(Tier.PLUS, "life.checkin.unlimited") is True
    assert check_feature_access(Tier.PLUS, "health.doc.translate") is True


def test_premium_tier_allowed_for_premium_only_features() -> None:
    assert check_feature_access(Tier.PREMIUM, "mind.coach.monthly") is True
    assert check_feature_access(Tier.PLUS, "mind.coach.monthly") is False
    assert check_feature_access(Tier.FREE, "mind.coach.monthly") is False


def test_unknown_feature_is_closed_by_default() -> None:
    assert check_feature_access(Tier.PREMIUM, "nonexistent.feature.xyz") is False


# --------------------------- Tier parsing --------------------------- #


def test_get_tier_parses_known_strings() -> None:
    assert get_tier("free") is Tier.FREE
    assert get_tier("plus") is Tier.PLUS
    assert get_tier("premium") is Tier.PREMIUM


def test_get_tier_handles_case_insensitivity() -> None:
    assert get_tier("FREE") is Tier.FREE
    assert get_tier("Plus") is Tier.PLUS


def test_get_tier_defaults_to_free_for_unknown_or_empty() -> None:
    assert get_tier(None) is Tier.FREE
    assert get_tier("") is Tier.FREE
    assert get_tier("nonexistent") is Tier.FREE
