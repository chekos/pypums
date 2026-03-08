"""ACS Migration Flows data retrieval via the Census API."""

from pathlib import Path

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import _resolve_state_fips
from pypums.api.key import census_api_key
from pypums.cache import CensusCache

# Core flow estimate columns and their MOE counterparts.
_FLOW_ESTIMATE_COLS = ["MOVEDIN", "MOVEDOUT", "MOVEDNET"]
_FLOW_MOE_COLS = ["MOVEDIN_M", "MOVEDOUT_M", "MOVEDNET_M"]

# All numeric flow columns.
_FLOW_NUMERIC_COLS = _FLOW_ESTIMATE_COLS + _FLOW_MOE_COLS

# Valid geography levels for migration flows.
_VALID_GEOGRAPHIES = frozenset(
    {
        "county",
        "metropolitan statistical area",
    }
)

# Z-scores for MOE confidence levels (same as acs.py).
_Z_SCORES: dict[int, float] = {
    90: 1.645,
    95: 1.960,
    99: 2.576,
}

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
        If True, add ``*_label`` columns with human-readable names
        for each breakdown dimension using the ``mig_recodes`` lookup.
    year
        Data year (default 2019).
    output
        ``"tidy"`` (default) or ``"wide"``.
    state
        State FIPS code or abbreviation.
    county
        County FIPS code.
    msa
        Metropolitan Statistical Area code.
    geometry
        If True, return a GeoDataFrame with shapes for the origin geography.
    moe_level
        Confidence level for MOE: 90, 95, or 99 (default 90).
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
    if output not in ("tidy", "wide"):
        raise ValueError(f"output must be 'tidy' or 'wide', got {output!r}")
    if moe_level not in _Z_SCORES:
        raise ValueError(
            f"moe_level must be one of {sorted(_Z_SCORES)}, got {moe_level!r}"
        )

    api_key = census_api_key(key) if key else census_api_key()

    url = f"{CENSUS_API_BASE}/{year}/acs/flows"

    # Default flow variables.
    get_vars = [
        "FULL1_NAME",
        "FULL2_NAME",
        "MOVEDIN",
        "MOVEDIN_M",
        "MOVEDOUT",
        "MOVEDOUT_M",
        "MOVEDNET",
        "MOVEDNET_M",
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

    # Build cache key from all parameters that affect the result.
    vars_str = ",".join(variables) if variables is not None else ""
    breakdown_str = ",".join(breakdown) if breakdown is not None else ""
    cache_key = (
        f"flows_{year}_{geography}_{state}_{county}"
        f"_{msa}_{vars_str}_{breakdown_str}"
        f"_{output}_{moe_level}"
    )

    # Check cache before calling API.
    disk_cache = CensusCache(_DEFAULT_CACHE_DIR) if cache_table else None
    if disk_cache is not None:
        cached = disk_cache.get(cache_key)
        if cached is not None:
            return cached

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

    # Scale MOE if needed (Census API returns MOE at 90% confidence).
    if moe_level != 90:
        scale_factor = _Z_SCORES[moe_level] / _Z_SCORES[90]
        moe_cols_present = [c for c in _FLOW_MOE_COLS if c in df.columns]
        df[moe_cols_present] = df[moe_cols_present] * scale_factor

    # Build GEOID for origin geography (state1 + county1).
    geo_cols = [c for c in ("state1", "county1") if c in df.columns]
    if geo_cols:
        df["GEOID"] = df[geo_cols].apply(lambda row: "".join(row), axis=1)

    # Add human-readable labels for breakdown dimensions.
    if breakdown_labels and breakdown is not None:
        from pypums.datasets.mig_recodes import MIG_RECODE_LABELS

        for dim in breakdown:
            dim_upper = dim.upper()
            if dim_upper in MIG_RECODE_LABELS and dim_upper in df.columns:
                # Census API returns codes as strings (possibly zero-padded),
                # so map directly without converting to avoid padding mismatch.
                df[f"{dim_upper}_label"] = df[dim_upper].map(
                    MIG_RECODE_LABELS[dim_upper]
                )

    # Format output.
    if output == "tidy":
        # Identify id columns (non-numeric, non-geo FIPS columns).
        fips_cols = {"state1", "county1", "state2", "county2"}
        id_cols = [
            c for c in df.columns if c not in _FLOW_NUMERIC_COLS and c not in fips_cols
        ]

        est_cols = [c for c in _FLOW_ESTIMATE_COLS if c in df.columns]
        moe_cols = [c for c in _FLOW_MOE_COLS if c in df.columns]

        if est_cols:
            est_long = df.melt(
                id_vars=id_cols,
                value_vars=est_cols,
                var_name="variable",
                value_name="estimate",
            )
            moe_long = df.melt(
                id_vars=id_cols,
                value_vars=moe_cols,
                var_name="_moe_var",
                value_name="moe",
            )
            # Map MOE variable back to estimate variable name.
            moe_long["variable"] = moe_long["_moe_var"].str.replace(
                "_M$", "", regex=True
            )

            df = est_long.merge(
                moe_long[id_cols + ["variable", "moe"]],
                on=id_cols + ["variable"],
            )

    if geometry:
        from pypums.spatial import attach_geometry

        # Map flows geography names to spatial module names.
        geo_name = geography
        if geography == "metropolitan statistical area":
            geo_name = "cbsa"
        df = attach_geometry(df, geo_name, state=state, year=year)

    if disk_cache is not None:
        disk_cache.set(cache_key, df, ttl_seconds=86400)

    return df
