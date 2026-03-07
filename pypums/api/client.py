"""Shared Census API HTTP client."""

import httpx

CENSUS_API_BASE = "https://api.census.gov/data"
CENSUS_TIMEOUT = 30


def call_census_api(url: str, params: dict) -> list[list[str]]:
    """Make an HTTP request to the Census API and return JSON rows."""
    response = httpx.get(url, params=params, timeout=CENSUS_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_json(url: str) -> dict:
    """Fetch JSON from a Census API endpoint."""
    response = httpx.get(url, timeout=CENSUS_TIMEOUT)
    response.raise_for_status()
    return response.json()
