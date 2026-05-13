"""
Crisis detector tests.

Phase 1: confirms stub contract + that hotline data is complete.
Phase 2: parametrizes trigger phrases (EN + RU) and asserts is_crisis=True.

The detector is the most safety-critical module. 100% branch coverage
is enforced by `pytest tests/crisis/ --cov=src/crisis --cov-fail-under=100`.
"""

from __future__ import annotations

import pytest

from src.crisis.detector import REGEX_TRIGGERS, is_crisis
from src.crisis.hotlines import HotlineEntry, get_hotlines


# ----------------------- Detector stub contract ----------------------- #


def test_is_crisis_stub_returns_false_for_safe_text() -> None:
    assert is_crisis("hello, how are you?") is False


def test_is_crisis_handles_empty_string() -> None:
    assert is_crisis("") is False


def test_is_crisis_handles_lang_param() -> None:
    # Phase 1 stub ignores lang; ensure no crash.
    assert is_crisis("test", lang="ru") is False
    assert is_crisis("test", lang="en") is False
    assert is_crisis("test", lang="auto") is False


def test_phase_2_regex_triggers_placeholder_is_list() -> None:
    """Phase 1: list is empty. Phase 2 fills it - test still asserts type."""
    assert isinstance(REGEX_TRIGGERS, list)
    for entry in REGEX_TRIGGERS:  # Phase 2: each entry is (pattern, category)
        assert isinstance(entry, tuple) and len(entry) == 2


# ----------------------- Hotline data completeness ----------------------- #


_VALID_TYPES = {"suicide_crisis", "emergency", "children", "domestic_violence"}


@pytest.mark.parametrize(
    "country",
    ["RU", "US", "GB", "DE", "FR", "ES", "IT", "KZ", "BY", "UA"],
)
def test_hotline_data_is_complete_per_country(country: str) -> None:
    entries = get_hotlines(country)
    assert len(entries) >= 2, f"{country} must have at least suicide_crisis + emergency"
    types_present = {e.type for e in entries}
    assert "emergency" in types_present, f"{country} missing emergency number"
    for entry in entries:
        assert entry.country == country
        assert entry.name
        assert entry.number
        assert entry.type in _VALID_TYPES


def test_hotline_unknown_country_returns_union() -> None:
    entries = get_hotlines("ZZ")
    countries = {e.country for e in entries}
    # Union fallback: RU + US + GB
    assert {"RU", "US", "GB"}.issubset(countries)


def test_hotline_none_returns_union() -> None:
    entries = get_hotlines(None)
    assert len(entries) > 3
    countries = {e.country for e in entries}
    assert {"RU", "US", "GB"}.issubset(countries)


def test_hotline_entry_is_frozen_dataclass() -> None:
    entry = HotlineEntry("RU", "Test", "123", "suicide_crisis")
    with pytest.raises(Exception):
        entry.number = "999"  # type: ignore[misc]
