"""
Crisis hotline directory.

Geo-mapped to country code (ISO 3166-1 alpha-2). Unknown country falls back to
the union of RU + US + EU hotlines so the user always has a working number.

Data source: GUARDRAILS.md section 1.3. Update only via security-reviewer-
approved PR.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HotlineEntry:
    country: str  # ISO 3166-1 alpha-2 (e.g. "RU"), or "INT" for international
    name: str
    number: str
    type: str  # "suicide_crisis" | "emergency" | "children" | "domestic_violence"


_HOTLINES: dict[str, list[HotlineEntry]] = {
    "RU": [
        HotlineEntry("RU", "Children & Adolescents Helpline", "8-800-2000-122", "children"),
        HotlineEntry("RU", "Psychological Crisis Helpline", "8-499-791-20-50", "suicide_crisis"),
        HotlineEntry("RU", "Emergency Services", "112", "emergency"),
    ],
    "US": [
        HotlineEntry("US", "Suicide & Crisis Lifeline", "988", "suicide_crisis"),
        HotlineEntry("US", "Emergency Services", "911", "emergency"),
    ],
    "GB": [
        HotlineEntry("GB", "Samaritans", "116 123", "suicide_crisis"),
        HotlineEntry("GB", "Emergency Services", "112", "emergency"),
    ],
    "DE": [
        HotlineEntry("DE", "Telefonseelsorge", "0800 111 0 111", "suicide_crisis"),
        HotlineEntry("DE", "Emergency Services", "112", "emergency"),
    ],
    "FR": [
        HotlineEntry("FR", "SOS Amitie", "09 72 39 40 50", "suicide_crisis"),
        HotlineEntry("FR", "Emergency Services", "112", "emergency"),
    ],
    "ES": [
        HotlineEntry("ES", "Telefono de la Esperanza", "717 003 717", "suicide_crisis"),
        HotlineEntry("ES", "Emergency Services", "112", "emergency"),
    ],
    "IT": [
        HotlineEntry("IT", "Telefono Amico", "02 2327 2327", "suicide_crisis"),
        HotlineEntry("IT", "Emergency Services", "112", "emergency"),
    ],
    "KZ": [
        HotlineEntry("KZ", "Psychological Helpline", "150", "suicide_crisis"),
        HotlineEntry("KZ", "Emergency Services", "112", "emergency"),
    ],
    "BY": [
        HotlineEntry("BY", "Belarusian Crisis Helpline", "8-801-100-1611", "suicide_crisis"),
        HotlineEntry("BY", "Emergency Services", "112", "emergency"),
    ],
    "UA": [
        HotlineEntry("UA", "Lifeline Ukraine", "7333", "suicide_crisis"),
        HotlineEntry("UA", "Emergency Services", "112", "emergency"),
    ],
}


def get_hotlines(country_code: str | None) -> list[HotlineEntry]:
    """
    Return the prioritized hotline list for a country.

    Unknown / None country falls back to RU + US + Samaritans (GB) union so
    the user always sees a working number.
    """
    if country_code:
        cc = country_code.strip().upper()
        if cc in _HOTLINES:
            return _HOTLINES[cc]
    # Fallback for unknown geography
    return [
        *_HOTLINES["RU"],
        *_HOTLINES["US"],
        *_HOTLINES["GB"],
    ]
