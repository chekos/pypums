"""ACS 5-year geography availability reference.

Provides information about which geographies are available for
ACS 5-year estimates, fetched from the Census API geography
endpoint with caching.
"""

from pathlib import Path

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, fetch_json
from pypums.cache import CensusCache

_DEFAULT_CACHE_DIR = Path.home() / ".pypums" / "cache" / "geography"


def _fetch_geography_json(url: str) -> dict:
    """Mockable wrapper around ``fetch_json``."""
    return fetch_json(url)


def acs5_geography(
    year: int = 2023,
    cache: bool = True,
) -> pd.DataFrame:
    """Load available geographies for the ACS 5-year dataset.

    Fetches the geography reference from the Census API and returns
    a DataFrame describing available geography levels.

    Parameters
    ----------
    year
        Data year (default 2023).
    cache
        If True, cache the result on disk for subsequent calls.

    Returns
    -------
    pd.DataFrame
        Columns: ``name``, ``hierarchy``, ``requires``.
    """
    cache_key = f"acs5_geography_{year}"
    disk_cache = CensusCache(_DEFAULT_CACHE_DIR) if cache else None

    if disk_cache is not None:
        cached = disk_cache.get(cache_key)
        if cached is not None:
            return cached

    url = f"{CENSUS_API_BASE}/{year}/acs/acs5/geography.json"
    raw = _fetch_geography_json(url)

    fips_list = raw.get("fips", [])
    rows = []
    for geo in fips_list:
        requires = [
            req.get("name", "") for req in geo.get("requires", geo.get("wildcard", []))
        ]
        rows.append(
            {
                "name": geo.get("name", ""),
                "hierarchy": geo.get("geoLevelDisplay", ""),
                "requires": ", ".join(requires) if requires else "",
            }
        )

    df = pd.DataFrame(rows)

    if disk_cache is not None:
        disk_cache.set(cache_key, df)

    return df
