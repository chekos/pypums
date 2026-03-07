"""Population Estimates Program data retrieval via the Census API."""

import pandas as pd
from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import build_geography_query
from pypums.api.key import census_api_key

# Product-to-dataset mapping for PEP.
_PRODUCT_DATASETS: dict[str, str] = {
    "population": "pep/population",
    "components": "pep/components",
    "housing": "pep/housing",
    "characteristics": "pep/charagegroups",
}

# Geography columns for GEOID construction.
_GEO_COL_ORDER = ["state", "county"]


def _call_census_api(url: str, params: dict) -> list[list[str]]:
    """Thin wrapper so tests can mock ``pypums.estimates._call_census_api``."""
    return call_census_api(url, params)


def get_estimates(
    geography: str,
    *,
    product: str | None = None,
    variables: str | list[str] | None = None,
    breakdown: str | list[str] | None = None,
    breakdown_labels: bool = False,
    vintage: int = 2023,
    year: int | None = None,
    state: str | None = None,
    county: str | None = None,
    time_series: bool = False,
    output: str = "tidy",
    geometry: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Retrieve Population Estimates Program data from the Census API.

    Parameters
    ----------
    geography
        Geography level (e.g. ``"state"``, ``"county"``).
    product
        Estimates product: ``"population"``, ``"components"``,
        ``"housing"``, or ``"characteristics"``.
    variables
        Variable ID or list of IDs to request.
    breakdown
        Breakdown dimensions (e.g. ``"AGEGROUP"``, ``"SEX"``).
    breakdown_labels
        If True, include human-readable breakdown labels.
    vintage
        Vintage year for the estimates (default 2023).
    year
        Specific data year within the vintage.
    state
        State FIPS code or abbreviation.
    county
        County FIPS code.
    time_series
        If True, return data across multiple years.
    output
        ``"tidy"`` (default) or ``"wide"``.
    geometry
        If True, return a GeoDataFrame with shapes.
    show_call
        If True, print the API URL.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Population estimates data.
    """
    api_key = census_api_key(key) if key else census_api_key()
    for_clause, in_clause = build_geography_query(geography, state=state, county=county)

    # Determine the dataset path.
    dataset = _PRODUCT_DATASETS.get(product or "population", "pep/population")

    url = f"{CENSUS_API_BASE}/{vintage}/{dataset}"

    # Build variable list.
    if variables is not None:
        if isinstance(variables, str):
            variables = [variables]
        get_vars = ",".join(["NAME"] + list(variables))
    else:
        get_vars = "NAME"

    params: dict[str, str] = {
        "get": get_vars,
        "for": for_clause,
        "key": api_key,
    }
    if in_clause is not None:
        params["in"] = in_clause

    # Add breakdown parameters.
    if breakdown is not None:
        if isinstance(breakdown, str):
            breakdown = [breakdown]
        for dim in breakdown:
            params[dim] = "*"

    if year is not None:
        params["YEAR"] = str(year)

    if show_call:
        print(f"Census API call: {url}")
        print(f"  Parameters: {params}")

    data = _call_census_api(url, params)

    # Convert JSON rows to DataFrame.
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)

    # Build GEOID from FIPS columns.
    geo_cols = [c for c in _GEO_COL_ORDER if c in df.columns]
    if geo_cols:
        df["GEOID"] = df[geo_cols].apply(lambda row: "".join(row), axis=1)

    # Convert numeric columns (everything except NAME and geo columns).
    geo_set = frozenset(_GEO_COL_ORDER)
    numeric_cols = [c for c in df.columns if c not in geo_set and c not in ("NAME", "GEOID")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if geometry:
        from pypums.spatial import attach_geometry

        df = attach_geometry(df, geography, state=state, year=vintage)

    return df
