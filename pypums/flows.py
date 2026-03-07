"""ACS Migration Flows data retrieval via the Census API."""

from pathlib import Path

import pandas as pd
from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import _resolve_state_fips
from pypums.api.key import census_api_key
from pypums.cache import CensusCache

# Core flow columns that should be numeric.
_FLOW_NUMERIC_COLS = [
    "MOVEDIN", "MOVEDIN_M",
    "MOVEDOUT", "MOVEDOUT_M",
    "MOVEDNET", "MOVEDNET_M",
]

# Valid geography levels for migration flows.
_VALID_GEOGRAPHIES = frozenset({
    "county", "metropolitan statistical area",
})

_DEFAULT_CACHE_DIR = Path.home() / ".pypums" / "cache" / "api"


def _call_census_api(url: str, params: dict) -> list[list[str]]:
    """Thin wrapper so tests can mock ``pypums.flows._call_census_api``."""
    return call_census_api(url, params)


def get_flows(
    geography: str,
    *,
    variables: str | list[str] | None = None,
    breakdown: str | list[str] | None = None,
    breakdown_labels: bool = False,
    year: int = 2019,
    output: str = "tidy",
    state: str | None = None,
    county: str | None = None,
    msa: str | None = None,
    geometry: bool = False,
    moe_level: int = 90,
    cache_table: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Retrieve ACS Migration Flows data from the Census API.

    Parameters
    ----------
    geography
        Geography level (e.g. ``"county"``, ``"metropolitan statistical area"``).
    variables
        Variable ID or list of IDs to request.
    breakdown
        Breakdown dimensions for flow characteristics.
    breakdown_labels
        If True, include human-readable breakdown labels.
        Not yet implemented.
    year
        Data year (default 2019).
    output
        ``"tidy"`` (default) or ``"wide"``.
        Not yet implemented — currently returns wide format only.
    state
        State FIPS code or abbreviation.
    county
        County FIPS code.
    msa
        Metropolitan Statistical Area code.
    geometry
        If True, return a GeoDataFrame with shapes.
        Not yet implemented for flows.
    moe_level
        Confidence level for MOE: 90, 95, or 99 (default 90).
        Not yet implemented — MOE columns are returned as-is at 90%.
    cache_table
        If True, cache the API response locally to avoid redundant calls.
    show_call
        If True, print the API URL.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Migration flows data with MOVEDIN, MOVEDOUT, MOVEDNET columns.
    """
    if geography not in _VALID_GEOGRAPHIES:
        raise ValueError(
            f"geography must be one of {sorted(_VALID_GEOGRAPHIES)}, got {geography!r}"
        )

    api_key = census_api_key(key) if key else census_api_key()

    url = f"{CENSUS_API_BASE}/{year}/acs/flows"

    # Default flow variables.
    get_vars = [
        "FULL1_NAME", "FULL2_NAME",
        "MOVEDIN", "MOVEDIN_M",
        "MOVEDOUT", "MOVEDOUT_M",
        "MOVEDNET", "MOVEDNET_M",
    ]

    # Add user-requested variables.
    if variables is not None:
        if isinstance(variables, str):
            variables = [variables]
        for v in variables:
            if v not in get_vars:
                get_vars.append(v)

    params: dict[str, str] = {
        "get": ",".join(get_vars),
        "key": api_key,
    }

    # Build geography filter.
    if geography == "county" and state is not None:
        state_fips = _resolve_state_fips(state)
        if county is not None:
            params["for"] = f"county:{county}"
            params["in"] = f"state:{state_fips}"
        else:
            params["for"] = "county:*"
            params["in"] = f"state:{state_fips}"
    elif geography == "county":
        params["for"] = "county:*"
    else:
        params["for"] = f"{geography}:*"

    if msa is not None:
        params["MSA"] = msa

    # Add breakdown parameters.
    if breakdown is not None:
        if isinstance(breakdown, str):
            breakdown = [breakdown]
        for dim in breakdown:
            params[dim] = "*"

    if show_call:
        print(f"Census API call: {url}")
        print(f"  Parameters: {params}")

    data = _call_census_api(url, params)

    # Convert JSON rows to DataFrame.
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)

    # Convert numeric columns.
    for col in _FLOW_NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if cache_table:
        cache_key = f"flows_{year}_{geography}_{state}_{county}_{msa}"
        disk_cache = CensusCache(_DEFAULT_CACHE_DIR)
        disk_cache.set(cache_key, df, ttl_seconds=86400)

    return df
