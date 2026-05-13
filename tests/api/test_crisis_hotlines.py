"""
Crisis-hotlines endpoint - GUARDRAILS critical path.

Tests cover:
- Every supported country code returns its own hotline list
- Unknown / no country falls back to RU + US + GB union
- Endpoint is public (works with NO auth header)
- Each entry has all required fields (country, name, number, type)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "country",
    ["RU", "US", "GB", "DE", "FR", "ES", "IT", "KZ", "BY", "UA"],
)
def test_hotlines_per_supported_country(client: TestClient, country: str) -> None:
    response = client.get(f"/api/crisis/hotlines?country={country}")
    assert response.status_code == 200
    body = response.json()
    assert body["country"] == country
    assert len(body["entries"]) >= 2
    for entry in body["entries"]:
        assert entry["country"] == country
        assert entry["name"]
        assert entry["number"]
        assert entry["type"] in {
            "suicide_crisis",
            "emergency",
            "children",
            "domestic_violence",
        }


def test_hotlines_unknown_country_falls_back_to_union(client: TestClient) -> None:
    response = client.get("/api/crisis/hotlines?country=ZZ")
    assert response.status_code == 200
    body = response.json()
    # Fallback shows union of RU + US + GB
    countries = {e["country"] for e in body["entries"]}
    assert {"RU", "US", "GB"}.issubset(countries)


def test_hotlines_no_country_falls_back(client: TestClient) -> None:
    response = client.get("/api/crisis/hotlines")
    assert response.status_code == 200
    body = response.json()
    assert body["country"] is None
    countries = {e["country"] for e in body["entries"]}
    assert {"RU", "US", "GB"}.issubset(countries)


def test_hotlines_endpoint_is_public(client: TestClient) -> None:
    """GUARDRAILS section 6: no paywall on crisis support."""
    # Explicitly no Authorization header
    response = client.get("/api/crisis/hotlines?country=RU")
    assert response.status_code == 200
