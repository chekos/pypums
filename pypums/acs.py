"""American Community Survey data retrieval via the Census API."""

from __future__ import annotations

import httpx
import pandas as pd

from pypums.api.geography import build_geography_query
from pypums.api.key import census_api_key

_CENSUS_API_BASE = "https://api.census.gov/data"

# Z-scores for MOE confidence levels.
_Z_SCORES: dict[int, float] = {
    90: 1.645,
    95: 1.960,
    99: 2.576,
}

# Geography columns that appear in Census API responses.
_GEO_COLUMNS = frozenset({
    "state", "county", "tract", "block group", "block",
    "place", "congressional district",
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
    "us", "region", "division", "county subdivision",
})


def _call_census_api(url: str, params: dict) -> list[list[str]]:
    """Make an HTTP request to the Census API and return JSON rows."""
    response = httpx.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_acs(
    geography: str,
    variables: str | list[str] | None = None,
    table: str | None = None,
    state: str | None = None,
    county: str | None = None,
    year: int = 2023,
    output: str = "tidy",
    moe_level: int = 90,
    summary_var: str | None = None,
    geometry: bool = False,
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
    output
        ``"tidy"`` (default) or ``"wide"``.
    moe_level
        Confidence level for MOE: 90, 95, or 99 (default 90).
    summary_var
        Variable ID to include as denominator columns.
    geometry
        If True, return a GeoDataFrame with shapes.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Census data in tidy or wide format.
    """
    api_key = census_api_key(key) if key else census_api_key()
    for_clause, in_clause = build_geography_query(
        geography, state=state, county=county,
    )

    # Build the variable list for the API request.
    if variables is not None:
        if isinstance(variables, str):
            variables = [variables]
        # Census API needs E/M suffixes for ACS.
        api_vars: list[str] = []
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

    url = f"{_CENSUS_API_BASE}/{year}/acs/acs5"
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

    # Build GEOID from FIPS columns.
    geo_cols = [c for c in df.columns if c in _GEO_COLUMNS]
    if geo_cols:
        df["GEOID"] = df[geo_cols].apply(lambda row: "".join(row), axis=1)

    # Identify estimate and MOE columns.
    estimate_cols = [c for c in df.columns if c.endswith("E") and c != "NAME"]
    moe_cols = [c for c in df.columns if c.endswith("M")]

    # Convert to numeric.
    for col in estimate_cols + moe_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Scale MOE if needed.
    if moe_level != 90 and moe_level in _Z_SCORES:
        scale_factor = _Z_SCORES[moe_level] / _Z_SCORES[90]
        for col in moe_cols:
            df[col] = df[col] * scale_factor

    if output == "wide":
        keep_cols = ["GEOID", "NAME"] + estimate_cols + moe_cols
        result = df[[c for c in keep_cols if c in df.columns]]
    else:
        # Tidy format: melt to one row per geography x variable.
        base_vars = list(dict.fromkeys(c[:-1] for c in estimate_cols))
        tidy_rows = []
        for _, row in df.iterrows():
            for var in base_vars:
                est_col = f"{var}E"
                moe_col = f"{var}M"
                tidy_row: dict = {
                    "GEOID": row.get("GEOID", ""),
                    "NAME": row["NAME"],
                    "variable": var,
                    "estimate": row.get(est_col),
                    "moe": row.get(moe_col),
                }
                if summary_var is not None:
                    tidy_row["summary_est"] = row.get(f"{summary_var}E")
                    tidy_row["summary_moe"] = row.get(f"{summary_var}M")
                tidy_rows.append(tidy_row)

        result = pd.DataFrame(tidy_rows)

    if geometry:
        from pypums.spatial import attach_geometry

        result = attach_geometry(result, geography, state=state, year=year)

    return result
