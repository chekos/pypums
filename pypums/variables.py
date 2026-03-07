"""Census variable discovery and metadata."""

import httpx
import pandas as pd

_CENSUS_API_BASE = "https://api.census.gov/data"

# Module-level in-memory cache for variable tables.
_cache: dict[tuple[int, str], pd.DataFrame] = {}


def _fetch_variables_json(url: str) -> dict:
    """Fetch variable definitions JSON from the Census API."""
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def load_variables(
    year: int,
    dataset: str,
    cache: bool = False,
) -> pd.DataFrame:
    """Load Census variable metadata for a given dataset and year.

    Parameters
    ----------
    year
        Census data year (e.g. 2023).
    dataset
        Dataset identifier (e.g. ``"acs5"``, ``"acs1"``, ``"pl"``,
        ``"acs5/subject"``, ``"acs5/profile"``).
    cache
        If True, cache the result in memory for subsequent calls.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``name``, ``label``, ``concept``.
    """
    cache_key = (year, dataset)

    if cache and cache_key in _cache:
        return _cache[cache_key]

    url = f"{_CENSUS_API_BASE}/{year}/{dataset}/variables.json"
    raw = _fetch_variables_json(url)

    variables = raw.get("variables", {})
    rows = [
        {
            "name": var_name,
            "label": var_info.get("label", ""),
            "concept": var_info.get("concept", ""),
        }
        for var_name, var_info in variables.items()
    ]

    df = pd.DataFrame(rows)

    if cache:
        _cache[cache_key] = df

    return df
