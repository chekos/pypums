"""Population Estimates Program data retrieval via the Census API."""

from pathlib import Path

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import build_geography_query
from pypums.api.key import census_api_key
from pypums.cache import CensusCache

# Valid output formats.
_VALID_OUTPUTS = frozenset({"tidy", "wide"})

# Human-readable labels for PEP breakdown dimension codes.
_BREAKDOWN_LABELS: dict[str, dict[str, str]] = {
    "AGEGROUP": {
        "0": "All ages",
        "1": "Age 0 to 4 years",
        "2": "Age 5 to 13 years",
        "3": "Age 14 to 17 years",
        "4": "Age 18 to 24 years",
        "5": "Age 25 to 44 years",
        "6": "Age 45 to 64 years",
        "7": "Age 65 years and over",
        "8": "Age 85 years and over",
        "9": "Age 0 to 17 years",
        "10": "Age 18 to 64 years",
        "11": "Age 18 years and over",
        "12": "Age 65 years and over",
        "13": "Under 18 years",
        "14": "5 to 13 years",
        "15": "14 to 17 years",
        "16": "18 to 64 years",
        "17": "16 years and over",
        "18": "Under 5 years",
        "29": "Age 0 to 14 years",
        "30": "Age 15 to 44 years",
        "31": "Age 16 years and over",
    },
    "SEX": {
        "0": "Both sexes",
        "1": "Male",
        "2": "Female",
    },
    "RACE": {
        "0": "All races",
        "1": "White alone",
        "2": "Black alone",
        "3": "American Indian and Alaska Native alone",
        "4": "Asian alone",
        "5": "Native Hawaiian and Other Pacific Islander alone",
        "6": "Two or more races",
        "7": "White alone or in combination",
        "8": "Black alone or in combination",
        "9": "American Indian and Alaska Native alone or in combination",
        "10": "Asian alone or in combination",
        "11": "Native Hawaiian and Other Pacific Islander alone or in combination",
    },
    "HISP": {
        "0": "Both Hispanic Origins",
        "1": "Non-Hispanic",
        "2": "Hispanic",
    },
}

# Product-to-dataset mapping for PEP.
_PRODUCT_DATASETS: dict[str, str] = {
    "population": "pep/population",
    "components": "pep/components",
    "housing": "pep/housing",
    "characteristics": "pep/charagegroups",
}

_VALID_PRODUCTS = frozenset(_PRODUCT_DATASETS)

# Geography columns for GEOID construction.
_GEO_COL_ORDER = ["state", "county"]

_DEFAULT_CACHE_DIR = Path.home() / ".pypums" / "cache" / "api"


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
    cache_table: bool = False,
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
        If True, add ``*_label`` columns with human-readable names
        for each breakdown dimension (e.g. ``AGEGROUP_label``).
    vintage
        Vintage year for the estimates (default 2023).
    year
        Specific data year within the vintage.
    state
        State FIPS code or abbreviation.
    county
        County FIPS code.
    time_series
        If True, request data across multiple years within the vintage
        by querying the ``/pep/population`` time-series endpoint and
        including ``DATE_CODE`` and ``DATE_DESC`` in the response.
    output
        ``"tidy"`` (default) or ``"wide"``.
    geometry
        If True, return a GeoDataFrame with shapes.
    cache_table
        If True, cache the API response locally to avoid redundant calls.
    show_call
        If True, print the API URL.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Population estimates data.
    """
    if output not in _VALID_OUTPUTS:
        raise ValueError(f"output must be 'tidy' or 'wide', got {output!r}")

    api_key = census_api_key(key) if key else census_api_key()
    for_clause, in_clause = build_geography_query(geography, state=state, county=county)

    # Validate product.
    resolved_product = product or "population"
    if resolved_product not in _VALID_PRODUCTS:
        raise ValueError(
            f"product must be one of {sorted(_VALID_PRODUCTS)},"
            f" got {resolved_product!r}"
        )
    dataset = _PRODUCT_DATASETS[resolved_product]

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

    if time_series:
        if resolved_product != "population":
            raise ValueError(
                "time_series=True is only supported for product='population'"
            )
        # Add date columns and request all dates within the vintage.
        params["get"] = params["get"] + ",DATE_CODE,DATE_DESC"
        params["DATE_CODE"] = "*"

    if year is not None:
        params["YEAR"] = str(year)

    # Build cache key from all parameters that affect the result.
    vars_str = ",".join(variables) if variables is not None else ""
    breakdown_str = ",".join(breakdown) if breakdown is not None else ""
    cache_key = (
        f"est_{vintage}_{resolved_product}_{geography}_{state}_{county}"
        f"_{year}_{vars_str}_{breakdown_str}_{output}"
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

    # Build GEOID from FIPS columns.
    geo_cols = [c for c in _GEO_COL_ORDER if c in df.columns]
    if geo_cols:
        df["GEOID"] = df[geo_cols].apply(lambda row: "".join(row), axis=1)

    # Convert numeric columns (everything except NAME and geo columns).
    geo_set = frozenset(_GEO_COL_ORDER)
    numeric_cols = [
        c for c in df.columns if c not in geo_set and c not in ("NAME", "GEOID")
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Add human-readable labels for breakdown dimensions.
    if breakdown_labels and breakdown is not None:
        for dim in breakdown:
            dim_upper = dim.upper()
            if dim_upper in _BREAKDOWN_LABELS and dim_upper in df.columns:
                df[f"{dim_upper}_label"] = (
                    df[dim_upper].astype(str).map(_BREAKDOWN_LABELS[dim_upper])
                )

    # Format output.
    if output == "tidy":
        id_cols = ["GEOID", "NAME"] if "GEOID" in df.columns else ["NAME"]
        # Include any breakdown columns in id_cols.
        excluded = geo_set | set(id_cols) | set(numeric_cols)
        breakdown_cols = [c for c in df.columns if c not in excluded]
        id_cols = id_cols + breakdown_cols

        value_cols = [c for c in numeric_cols if c in df.columns]
        if value_cols:
            df = df.melt(
                id_vars=id_cols,
                value_vars=value_cols,
                var_name="variable",
                value_name="value",
            )

    if geometry:
        from pypums.spatial import attach_geometry

        df = attach_geometry(df, geography, state=state, year=vintage)

    if disk_cache is not None:
        disk_cache.set(cache_key, df, ttl_seconds=86400)

    return df
