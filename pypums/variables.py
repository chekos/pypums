"""Census variable discovery and metadata."""

from pathlib import Path

import pandas as pd
from pypums.api.client import CENSUS_API_BASE, fetch_json
from pypums.cache import CensusCache

# Module-level in-memory cache for variable tables.
_cache: dict[tuple[int, str], pd.DataFrame] = {}

# Default persistent cache directory.
_DEFAULT_CACHE_DIR = Path.home() / ".pypums" / "cache"


def _fetch_variables_json(url: str) -> dict:
    """Fetch variable definitions JSON from the Census API."""
    return fetch_json(url)


def _get_persistent_cache() -> CensusCache:
    """Return a CensusCache instance for variable tables."""
    return CensusCache(_DEFAULT_CACHE_DIR / "variables")


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
        If True, cache the result both in memory and on disk for
        subsequent calls.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``name``, ``label``, ``concept``.
    """
    cache_key = (year, dataset)
    disk_key = f"{year}_{dataset.replace('/', '_')}"

    # 1. Check in-memory cache.
    if cache and cache_key in _cache:
        return _cache[cache_key]

    # 2. Check persistent disk cache.
    persistent = _get_persistent_cache() if cache else None
    if persistent is not None:
        cached_df = persistent.get(disk_key)
        if cached_df is not None:
            _cache[cache_key] = cached_df
            return cached_df

    # 3. Fetch from API.
    url = f"{CENSUS_API_BASE}/{year}/{dataset}/variables.json"
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

    # 4. Store in caches.
    if cache:
        _cache[cache_key] = df
        persistent.set(disk_key, df)

    return df
