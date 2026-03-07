"""PUMS variable dictionary — fetched from the Census API with caching.

Provides a searchable reference of PUMS variables with their names,
labels, and concepts.
"""

from pathlib import Path

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, fetch_json
from pypums.cache import CensusCache

_DEFAULT_CACHE_DIR = Path.home() / ".pypums" / "cache" / "pums_vars"


def _fetch_pums_variables_json(url: str) -> dict:
    """Mockable wrapper around ``fetch_json``."""
    return fetch_json(url)


def pums_variables(
    year: int = 2023,
    survey: str = "acs5",
    cache: bool = True,
) -> pd.DataFrame:
    """Load PUMS variable metadata from the Census API.

    Fetches the variable dictionary for the given year/survey and returns
    a DataFrame searchable by name, label, or concept.

    Parameters
    ----------
    year
        Data year (default 2023).
    survey
        ``"acs1"`` or ``"acs5"`` (default ``"acs5"``).
    cache
        If True, cache the result on disk for subsequent calls.

    Returns
    -------
    pd.DataFrame
        Columns: ``name``, ``label``, ``concept``, ``var_type``.
    """
    cache_key = f"pums_vars_{year}_{survey}"
    disk_cache = CensusCache(_DEFAULT_CACHE_DIR) if cache else None

    if disk_cache is not None:
        cached = disk_cache.get(cache_key)
        if cached is not None:
            return cached

    url = f"{CENSUS_API_BASE}/{year}/acs/{survey}/pums/variables.json"
    raw = _fetch_pums_variables_json(url)

    variables = raw.get("variables", {})
    rows = []
    for var_name, var_info in variables.items():
        rows.append(
            {
                "name": var_name,
                "label": var_info.get("label", ""),
                "concept": var_info.get("concept", ""),
                "var_type": var_info.get("predicateType", ""),
            }
        )

    df = pd.DataFrame(rows)

    if disk_cache is not None:
        # Cache indefinitely since PUMS variables rarely change within a year.
        disk_cache.set(cache_key, df)

    return df
