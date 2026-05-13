"""
Subscription tier definitions + feature gating.

Phase 1 lays out the gate map. Phase 5 wires real Stripe/YooKassa subscription
records into `get_tier`.

INVARIANT (GUARDRAILS.md section 6): crisis features always work regardless of
tier - never paywalled. The `check_feature_access` function enforces this with
an explicit early return.
"""

from __future__ import annotations

from enum import Enum


class Tier(str, Enum):
    FREE = "free"
    PLUS = "plus"
    PREMIUM = "premium"


# Features that are ALWAYS allowed, regardless of tier.
ALWAYS_ALLOWED: frozenset[str] = frozenset(
    {
        "crisis.hotlines",
        "crisis.detect",
        "crisis.acknowledge",
        "auth.signin",
        "auth.signout",
        "settings.export",
        "settings.delete",
    }
)


# Feature -> minimum tier required.
FEATURE_GATES: dict[str, frozenset[Tier]] = {
    # Life pillar
    "life.checkin.daily": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "life.checkin.unlimited": frozenset({Tier.PLUS, Tier.PREMIUM}),
    "life.weekly_review": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "life.history.30d": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "life.history.unlimited": frozenset({Tier.PLUS, Tier.PREMIUM}),
    "life.patterns.basic": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "life.patterns.deep": frozenset({Tier.PLUS, Tier.PREMIUM}),
    # Mind pillar
    "mind.reflection.5_per_week": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "mind.reflection.unlimited": frozenset({Tier.PLUS, Tier.PREMIUM}),
    "mind.coach.monthly": frozenset({Tier.PREMIUM}),
    # Health pillar
    "health.doc.translate": frozenset({Tier.PLUS, Tier.PREMIUM}),
    "health.visit.prep": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "health.triage": frozenset({Tier.FREE, Tier.PLUS, Tier.PREMIUM}),
    "health.meds.tracker": frozenset({Tier.PLUS, Tier.PREMIUM}),
    "health.chronic.log": frozenset({Tier.PLUS, Tier.PREMIUM}),
}


def check_feature_access(user_tier: Tier, feature: str) -> bool:
    """
    Return True if `user_tier` may access `feature`.

    INVARIANT: features in ALWAYS_ALLOWED return True regardless of tier.
    This enforces GUARDRAILS.md section 6 (no paywall on crisis support).
    """
    if feature in ALWAYS_ALLOWED:
        return True
    allowed = FEATURE_GATES.get(feature)
    if allowed is None:
        # Unknown features default to closed - safer than open.
        return False
    return user_tier in allowed


def get_tier(tier_str: str | None) -> Tier:
    """Parse a tier string (e.g. from User.tier column) to the enum, default FREE."""
    if not tier_str:
        return Tier.FREE
    try:
        return Tier(tier_str.lower())
    except ValueError:
        return Tier.FREE
