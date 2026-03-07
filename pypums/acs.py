"""American Community Survey data retrieval via the Census API."""

from pathlib import Path

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import build_geography_query
from pypums.api.key import census_api_key
from pypums.cache import CensusCache

_DEFAULT_CACHE_DIR = Path.home() / ".pypums" / "cache" / "api"

# Z-scores for MOE confidence levels.
_Z_SCORES: dict[int, float] = {
    90: 1.645,
    95: 1.960,
    99: 2.576,
}

# Geography columns in FIPS concatenation order.  The order matters because
# GEOID is built by joining these columns (e.g. state+county+tract).
_GEO_COL_ORDER = [
    "us",
    "region",
    "division",
    "state",
    "county",
    "county subdivision",
    "tract",
    "block group",
    "block",
    "place",
    "congressional district",
    "state legislative district (upper chamber)",
    "state legislative district (lower chamber)",
    "zip code tabulation area",
    "school district (unified)",
    "school district (elementary)",
    "school district (secondary)",
    "metropolitan statistical area/micropolitan statistical area",
    "combined statistical area",
    "public use microdata area",
    "american indian area/alaska native area/hawaiian home land",
]
_GEO_COLUMNS = frozenset(_GEO_COL_ORDER)


def _call_census_api(url: str, params: dict) -> list[list[str]]:
    """Thin wrapper so tests can mock ``pypums.acs._call_census_api``."""
    return call_census_api(url, params)


def get_acs(
    geography: str,
    variables: str | list[str] | None = None,
    table: str | None = None,
    state: str | None = None,
    county: str | None = None,
    year: int = 2023,
    survey: str = "acs5",
    output: str = "tidy",
    moe_level: int = 90,
    summary_var: str | None = None,
    geometry: bool = False,
    keep_geo_vars: bool = False,
    cache_table: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Retrieve American Community Survey data from the Census API.

    Parameters
    ----------
    geography
        Geography level (e.g. ``"state"``, ``"county"``, ``"tract"``).
    variables
        Variable ID or list of IDs (e.g. ``"B01001_001"``).
    table
        Census table ID (e.g. ``"B01001"``). Alternative to *variables*.
    state
        State FIPS code or abbreviation.
    county
        County FIPS code.
    year
        Data year (default 2023).
    survey
        ``"acs5"`` (default) or ``"acs1"``.
    output
        ``"tidy"`` (default) or ``"wide"``.
    moe_level
        Confidence level for MOE: 90, 95, or 99 (default 90).
    summary_var
        Variable ID to include as denominator columns.
    geometry
        If True, return a GeoDataFrame with shapes.
    keep_geo_vars
        If True, preserve the raw FIPS columns (state, county, tract,
        etc.) in the output alongside GEOID.
    cache_table
        If True, cache the API response locally to avoid redundant calls.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Census data in tidy or wide format.
    """
    if output not in ("tidy", "wide"):
        raise ValueError(f"output must be 'tidy' or 'wide', got {output!r}")
    if moe_level not in _Z_SCORES:
        raise ValueError(
            f"moe_level must be one of {sorted(_Z_SCORES)}, got {moe_level!r}"
        )

    api_key = census_api_key(key) if key else census_api_key()
    for_clause, in_clause = build_geography_query(geography, state=state, county=county)

    # Build the variable list for the API request.
    if variables is not None:
        if isinstance(variables, str):
            variables = [variables]
        # Census API needs E/M suffixes for ACS.
        api_vars = []
        for v in variables:
            api_vars.append(f"{v}E")
            api_vars.append(f"{v}M")
    elif table is not None:
        api_vars = [f"group({table})"]
    else:
        raise ValueError("Must provide either 'variables' or 'table'.")

    # Add summary variable if requested.
    if summary_var is not None:
        api_vars.append(f"{summary_var}E")
        api_vars.append(f"{summary_var}M")

    # Build a cache key from request parameters.
    cache_key = (
        f"acs_{year}_{survey}_{geography}_{state}_{county}"
        f"_{output}_{moe_level}_{summary_var}_{','.join(api_vars)}"
    )

    # Check cache before calling API.
    disk_cache = CensusCache(_DEFAULT_CACHE_DIR) if cache_table else None
    if disk_cache is not None:
        cached = disk_cache.get(cache_key)
        if cached is not None:
            return cached

    url = f"{CENSUS_API_BASE}/{year}/acs/{survey}"
    params: dict[str, str] = {
        "get": f"NAME,{','.join(api_vars)}",
        "for": for_clause,
        "key": api_key,
    }
    if in_clause is not None:
        params["in"] = in_clause

    data = _call_census_api(url, params)

    # Convert JSON rows to DataFrame.
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)

    # Build GEOID from FIPS columns in canonical order.
    geo_cols = [c for c in _GEO_COL_ORDER if c in df.columns]
    if geo_cols:
        df["GEOID"] = df[geo_cols].apply(lambda row: "".join(row), axis=1)

    # Identify estimate and MOE columns.
    estimate_cols = [c for c in df.columns if c.endswith("E") and c != "NAME"]
    moe_cols = [c for c in df.columns if c.endswith("M")]

    # Convert to numeric.
    for col in estimate_cols + moe_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Scale MOE if needed.
    if moe_level != 90:
        scale_factor = _Z_SCORES[moe_level] / _Z_SCORES[90]
        df[moe_cols] = df[moe_cols] * scale_factor

    # Determine which geo FIPS columns to keep.
    geo_cols_present = [c for c in _GEO_COL_ORDER if c in df.columns]
    extra_geo = geo_cols_present if keep_geo_vars else []

    if output == "wide":
        keep_cols = ["GEOID", "NAME"] + extra_geo + estimate_cols + moe_cols
        result = df[[c for c in keep_cols if c in df.columns]]
    else:
        # Tidy format: melt estimate and MOE columns separately, then merge.
        id_cols = ["GEOID", "NAME"] if "GEOID" in df.columns else ["NAME"]
        id_cols = id_cols + extra_geo

        # Exclude summary_var columns from the main melt.
        summary_est_col = f"{summary_var}E" if summary_var else None
        summary_moe_col = f"{summary_var}M" if summary_var else None
        main_est_cols = [c for c in estimate_cols if c != summary_est_col]
        main_moe_cols = [c for c in moe_cols if c != summary_moe_col]

        est_long = df.melt(
            id_vars=id_cols,
            value_vars=main_est_cols,
            var_name="_est_var",
            value_name="estimate",
        )
        est_long["variable"] = est_long["_est_var"].str[:-1]

        moe_long = df.melt(
            id_vars=id_cols,
            value_vars=main_moe_cols,
            var_name="_moe_var",
            value_name="moe",
        )
        moe_long["variable"] = moe_long["_moe_var"].str[:-1]

        result = est_long[id_cols + ["variable", "estimate"]].merge(
            moe_long[id_cols + ["variable", "moe"]],
            on=id_cols + ["variable"],
        )

        # Add summary variable columns if requested.
        if summary_var is not None and summary_est_col in df.columns:
            summary_df = df[id_cols + [summary_est_col, summary_moe_col]].rename(
                columns={
                    summary_est_col: "summary_est",
                    summary_moe_col: "summary_moe",
                },
            )
            result = result.merge(summary_df, on=id_cols)

    if geometry:
        from pypums.spatial import attach_geometry

        result = attach_geometry(result, geography, state=state, year=year)

    if disk_cache is not None:
        disk_cache.set(cache_key, result, ttl_seconds=86400)

    return result
