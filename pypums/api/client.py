"""Shared Census API HTTP client."""

import httpx

CENSUS_API_BASE = "https://api.census.gov/data"


def call_census_api(url: str, params: dict) -> list[list[str]]:
    """Make an HTTP request to the Census API and return JSON rows."""
    response = httpx.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
