"""FIPS codes for all US states and counties."""

from pathlib import Path

import pandas as pd

_DATA_DIR = Path(__file__).parent / "data"

fips_codes: pd.DataFrame = pd.read_csv(_DATA_DIR / "fips_codes.csv", dtype=str)


def lookup_fips(
    state: str | None = None,
    county: str | None = None,
) -> str:
    """Look up a FIPS code from a state or county name.

    Parameters
    ----------
    state
        State name (e.g. ``"California"``).
    county
        County name (e.g. ``"Los Angeles County"``). Requires *state*.

    Returns
    -------
    str
        The FIPS code: 2-digit state code, or state+county code.

    Raises
    ------
    ValueError
        If the state or county is not found.
    """
    if state is None:
        raise ValueError("state is required for FIPS lookup.")

    state_rows = fips_codes[fips_codes["state"].str.lower() == state.lower()]
    if state_rows.empty:
        raise ValueError(f"State not found: {state!r}")

    state_code = state_rows["state_code"].iloc[0]

    if county is None:
        return state_code

    county_rows = state_rows[state_rows["county"].str.lower() == county.lower()]
    if county_rows.empty:
        raise ValueError(f"County not found: {county!r} in state {state!r}")

    return state_code + county_rows["county_code"].iloc[0]


def lookup_name(
    state_code: str | None = None,
    county_code: str | None = None,
) -> str:
    """Look up a state or county name from FIPS code(s).

    Parameters
    ----------
    state_code
        2-digit state FIPS code (e.g. ``"06"``).
    county_code
        3-digit county FIPS code (e.g. ``"037"``). Requires *state_code*.

    Returns
    -------
    str
        The state name, or ``"County, State"`` if county_code is given.

    Raises
    ------
    ValueError
        If the code is not found.
    """
    if state_code is None:
        raise ValueError("state_code is required for name lookup.")

    state_rows = fips_codes[fips_codes["state_code"] == state_code]
    if state_rows.empty:
        raise ValueError(f"State code not found: {state_code!r}")

    state_name = state_rows["state"].iloc[0]

    if county_code is None:
        return state_name

    county_rows = state_rows[state_rows["county_code"] == county_code]
    if county_rows.empty:
        raise ValueError(
            f"County code not found: {county_code!r} in state {state_code!r}"
        )

    return f"{county_rows['county'].iloc[0]}, {state_name}"
