"""Census helper functions for summary files and population groups.

Provides ``summary_files()`` and ``get_pop_groups()`` for discovering
available Census Bureau data products.
"""

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, fetch_json


def _fetch_json(url: str) -> dict | list:
    """Thin wrapper so tests can mock ``pypums.census_helpers._fetch_json``."""
    return fetch_json(url)


def summary_files(
    year: int = 2020,
) -> pd.DataFrame:
    """List available summary files for a given Census year.

    Queries the Census API to discover which summary files (datasets)
    are available for a decennial census year.

    Parameters
    ----------
    year
        Census year (e.g. 2020, 2010).

    Returns
    -------
    pd.DataFrame
        Columns: ``dataset_name``, ``title``, ``description``.
    """
    url = f"{CENSUS_API_BASE}/{year}.json"
    raw = _fetch_json(url)

    datasets = raw.get("dataset", []) if isinstance(raw, dict) else []

    rows = []
    for ds in datasets:
        c_dataset = ds.get("c_dataset", [])
        # Only include decennial census datasets.
        if c_dataset and c_dataset[0].startswith("dec"):
            rows.append(
                {
                    "dataset_name": "/".join(c_dataset),
                    "title": ds.get("title", ""),
                    "description": ds.get("description", ""),
                }
            )

    return pd.DataFrame(rows, columns=["dataset_name", "title", "description"])


def get_pop_groups(
    year: int = 2020,
    state: str | None = None,
) -> pd.DataFrame:
    """List available population groups for decennial Census DHC-A data.

    Population groups are used with the ``pop_group`` parameter in
    ``get_decennial()`` to access disaggregated data by detailed
    race/ethnicity categories.

    Parameters
    ----------
    year
        Census year (default 2020).
    state
        State FIPS code to filter population groups (optional).

    Returns
    -------
    pd.DataFrame
        Columns: ``code``, ``label``.
    """
    # The DHC-A population groups endpoint.
    url = f"{CENSUS_API_BASE}/{year}/dec/dhc-a/popgroup.json"
    raw = _fetch_json(url)

    if not isinstance(raw, list) or len(raw) < 2:
        return pd.DataFrame(columns=["code", "label"])

    # Census API returns JSON rows: first row is headers, rest is data.
    headers = raw[0]
    rows = []
    state_col = None
    if state is not None:
        state_col = next((h for h in headers if h.lower() == "state"), None)

    for record in raw[1:]:
        row = dict(zip(headers, record, strict=True))
        rows.append(
            {
                "code": row.get("POP_GROUP", ""),
                "label": row.get("POP_GROUP_NAME", row.get("NAME", "")),
                "_state": row.get(state_col, "") if state_col else "",
            }
        )

    df = pd.DataFrame(rows)

    if state is not None and state_col is not None:
        df = df[df["_state"] == state].reset_index(drop=True)

    return df.drop(columns=["_state"], errors="ignore")
