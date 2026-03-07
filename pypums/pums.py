"""PUMS microdata retrieval via the Census API."""

import pandas as pd
from pypums.api.client import CENSUS_API_BASE, call_census_api
from pypums.api.geography import _resolve_state_fips
from pypums.api.key import census_api_key

# Standard PUMS weight and ID columns always requested.
_PUMS_BASE_VARS = ["SERIALNO", "SPORDER", "PWGTP", "ST", "PUMA"]

# Person replicate weight columns (PWGTP1..PWGTP80).
_PERSON_REP_WEIGHTS = [f"PWGTP{i}" for i in range(1, 81)]

# Housing replicate weight columns (WGTP1..WGTP80).
_HOUSING_REP_WEIGHTS = [f"WGTP{i}" for i in range(1, 81)]

# Common PUMS variable recode labels.
_PUMS_RECODES: dict[str, dict[str, str]] = {
    "SEX": {"1": "Male", "2": "Female"},
    "MAR": {
        "1": "Married",
        "2": "Widowed",
        "3": "Divorced",
        "4": "Separated",
        "5": "Never married",
    },
    "SCHL": {
        "01": "No schooling completed",
        "16": "Regular high school diploma",
        "20": "Associate's degree",
        "21": "Bachelor's degree",
        "22": "Master's degree",
        "24": "Doctorate degree",
    },
    "RAC1P": {
        "1": "White alone",
        "2": "Black or African American alone",
        "3": "American Indian alone",
        "6": "Asian alone",
        "9": "Two or More Races",
    },
    "HISP": {
        "01": "Not Spanish/Hispanic/Latino",
    },
    "ESR": {
        "1": "Civilian employed, at work",
        "2": "Civilian employed, with a job but not at work",
        "3": "Unemployed",
        "6": "Not in labor force",
    },
}


def _call_census_api(url: str, params: dict) -> list[list[str]]:
    """Thin wrapper so tests can mock ``pypums.pums._call_census_api``."""
    return call_census_api(url, params)


def get_pums(
    variables: str | list[str] | None = None,
    *,
    state: str | list[str] | None = None,
    puma: str | list[str] | None = None,
    year: int = 2023,
    survey: str = "acs5",
    variables_filter: dict[str, list | int | str] | None = None,
    rep_weights: str | None = None,
    recode: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Load PUMS microdata from the Census API.

    Parameters
    ----------
    variables
        PUMS variable name(s) to retrieve (e.g. ``"AGEP"``, ``["AGEP", "SEX"]``).
    state
        State abbreviation, name, or FIPS code. Required.
    puma
        PUMA code(s) to filter by.
    year
        Data year (default 2023).
    survey
        ``"acs1"`` or ``"acs5"`` (default ``"acs5"``).
    variables_filter
        Server-side variable filters as ``{var: value_or_list}``.
    rep_weights
        Include replicate weights: ``"person"``, ``"housing"``, or ``"both"``.
    recode
        If True, add ``*_label`` columns with human-readable values.
    show_call
        If True, print the API URL.
    key
        Census API key. Falls back to ``census_api_key()``.

    Returns
    -------
    pd.DataFrame
        Person- or housing-level microdata records.

    Raises
    ------
    ValueError
        If ``state`` is not provided.
    """
    if state is None:
        raise ValueError(
            "A state is required for get_pums(). "
            "Pass state='CA' or a FIPS code like state='06'."
        )

    api_key = census_api_key(key) if key else census_api_key()

    # Normalize variables.
    if variables is None:
        user_vars: list[str] = []
    elif isinstance(variables, str):
        user_vars = [variables]
    else:
        user_vars = list(variables)

    # Build the full variable list.
    all_vars = list(_PUMS_BASE_VARS)
    for v in user_vars:
        if v not in all_vars:
            all_vars.append(v)

    # Add replicate weights.
    if rep_weights in ("person", "both"):
        all_vars.extend(_PERSON_REP_WEIGHTS)
    if rep_weights in ("housing", "both"):
        all_vars.extend(_HOUSING_REP_WEIGHTS)

    # Resolve state FIPS.
    if isinstance(state, str):
        state_fips = _resolve_state_fips(state)
    else:
        state_fips = _resolve_state_fips(state[0])

    url = f"{CENSUS_API_BASE}/{year}/acs/{survey}/pums"
    params: dict[str, str] = {
        "get": ",".join(all_vars),
        "for": f"state:{state_fips}",
        "key": api_key,
    }

    # Add server-side filters.
    if variables_filter is not None:
        for var, val in variables_filter.items():
            if isinstance(val, list):
                params[var] = ",".join(str(v) for v in val)
            else:
                params[var] = str(val)

    # Add PUMA filter.
    if puma is not None:
        if isinstance(puma, str):
            params["PUMA"] = puma
        else:
            params["PUMA"] = ",".join(puma)

    data = _call_census_api(url, params)

    # Convert JSON rows to DataFrame.
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)

    # Convert numeric columns.
    numeric_candidates = ["PWGTP", "AGEP", "SPORDER"] + user_vars
    if rep_weights:
        numeric_candidates.extend(
            col for col in df.columns
            if col.startswith(("PWGTP", "WGTP")) and col not in numeric_candidates
        )
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Recode: add label columns for coded variables.
    if recode:
        for var in user_vars:
            if var in _PUMS_RECODES and var in df.columns:
                df[f"{var}_label"] = df[var].astype(str).map(_PUMS_RECODES[var])

    return df
