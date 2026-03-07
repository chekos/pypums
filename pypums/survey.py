"""Survey metadata retrieval from the Census API discovery endpoint."""

import pandas as pd

from pypums.api.client import CENSUS_API_BASE, fetch_json


def _fetch_data_json() -> dict:
    """Thin wrapper so tests can mock ``pypums.survey._fetch_data_json``."""
    return fetch_json(f"{CENSUS_API_BASE}.json")


def get_survey_metadata(
    year: int | None = None,
) -> pd.DataFrame:
    """Fetch available Census Bureau dataset metadata.

    Queries the Census API discovery endpoint
    (``https://api.census.gov/data.json``) and returns a DataFrame of
    available datasets, optionally filtered by year.

    Parameters
    ----------
    year
        If provided, filter to datasets for that vintage/year.

    Returns
    -------
    pd.DataFrame
        Columns: ``title``, ``description``, ``vintage``, ``dataset_name``,
        ``distribution_url``.
    """
    catalog = _fetch_data_json()

    datasets = catalog.get("dataset", [])

    rows = []
    for ds in datasets:
        vintage = ds.get("c_vintage")
        title = ds.get("title", "")
        description = ds.get("description", "")
        dataset_name = "/".join(ds.get("c_dataset", []))

        # Build the API distribution URL.
        dist_url = ""
        for dist in ds.get("distribution", []):
            if dist.get("accessURL"):
                dist_url = dist["accessURL"]
                break

        rows.append(
            {
                "title": title,
                "description": description,
                "vintage": int(vintage) if vintage is not None else None,
                "dataset_name": dataset_name,
                "distribution_url": dist_url,
            }
        )

    _COLUMNS = [
        "title",
        "description",
        "vintage",
        "dataset_name",
        "distribution_url",
    ]
    df = pd.DataFrame(rows, columns=_COLUMNS)

    if year is not None:
        df = df[df["vintage"] == year].reset_index(drop=True)

    return df
