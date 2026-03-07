"""Decennial Census data retrieval via the Census API."""

import pandas as pd
from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import build_geography_query
from pypums.api.key import census_api_key

# Default dataset by census year.
_YEAR_DATASETS: dict[int, str] = {
    2020: "dec/dhc",
    2010: "dec/sf1",
    2000: "dec/sf1",
}

# Geography columns that appear in Census API responses.
_GEO_COLUMNS = frozenset({
    "state", "county", "tract", "block group", "block",
    "place", "congressional district",
    "us", "region", "division", "county subdivision",
})


def _call_census_api(url: str, params: dict) -> list[list[str]]:
    """Thin wrapper so tests can mock ``pypums.decennial._call_census_api``."""
    return call_census_api(url, params)


def get_decennial(
    geography: str,
    variables: str | list[str] | None = None,
    table: str | None = None,
    state: str | None = None,
    county: str | None = None,
    year: int = 2020,
    output: str = "tidy",
    pop_group: str | None = None,
    geometry: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Retrieve Decennial Census data from the Census API.

    Parameters
    ----------
    geography
        Geography level (e.g. ``"state"``, ``"county"``).
    variables
        Variable ID or list of IDs (e.g. ``"P1_001N"``).
    table
        Census table ID. Alternative to *variables*.
    state
        State FIPS code or abbreviation.
    county
        County FIPS code.
    year
        Census year: 2000, 2010, or 2020 (default 2020).
    output
        ``"tidy"`` (default) or ``"wide"``.
    pop_group
        Population group code for DHC-A disaggregated data.
    geometry
        If True, return a GeoDataFrame with shapes.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Census data in tidy or wide format.
    """
    if output not in ("tidy", "wide"):
        raise ValueError(f"output must be 'tidy' or 'wide', got {output!r}")

    api_key = census_api_key(key) if key else census_api_key()
    for_clause, in_clause = build_geography_query(geography, state=state, county=county)

    # Select dataset.
    dataset = "dec/dhc-a" if pop_group is not None else _YEAR_DATASETS.get(year, "dec/dhc")

    # Build the variable list.
    if variables is not None:
        if isinstance(variables, str):
            variables = [variables]
        api_vars = list(variables)
    elif table is not None:
        api_vars = [f"group({table})"]
    else:
        raise ValueError("Must provide either 'variables' or 'table'.")

    url = f"{CENSUS_API_BASE}/{year}/{dataset}"
    params: dict[str, str] = {
        "get": f"NAME,{','.join(api_vars)}",
        "for": for_clause,
        "key": api_key,
    }
    if in_clause is not None:
        params["in"] = in_clause
    if pop_group is not None:
        params["POP_GROUP"] = pop_group

    data = _call_census_api(url, params)

    # Convert JSON rows to DataFrame.
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)

    # Build GEOID from FIPS columns.
    geo_cols = [c for c in df.columns if c in _GEO_COLUMNS]
    if geo_cols:
        df["GEOID"] = df[geo_cols].apply(lambda row: "".join(row), axis=1)

    # Identify variable columns (everything except NAME and geo columns).
    var_cols = [c for c in df.columns if c not in _GEO_COLUMNS and c not in ("NAME", "GEOID")]

    # Convert to numeric.
    for col in var_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if output == "wide":
        keep_cols = ["GEOID", "NAME"] + var_cols
        result = df[[c for c in keep_cols if c in df.columns]]
    else:
        # Tidy format: melt to one row per geography x variable.
        id_cols = ["GEOID", "NAME"] if "GEOID" in df.columns else ["NAME"]
        result = df.melt(
            id_vars=id_cols,
            value_vars=var_cols,
            var_name="variable",
            value_name="value",
        )

    if geometry:
        from pypums.spatial import attach_geometry

        result = attach_geometry(result, geography, state=state, year=year)

    return result
