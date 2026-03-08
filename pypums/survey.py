"""Survey metadata and survey design support.

Includes the Census API discovery endpoint for dataset metadata,
and ``to_survey()`` for converting PUMS data to a weighted survey
design object with replicate-weight standard error support.
"""

from __future__ import annotations

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


class SurveyDesign:
    """Lightweight survey design object for PUMS data with replicate weights.

    Wraps a PUMS DataFrame and its weight/replicate-weight columns to
    compute weighted estimates and replicate-weight standard errors
    using the successive differences replication (SDR) method.

    Parameters
    ----------
    df
        PUMS DataFrame (from ``get_pums()``).
    weight
        Name of the main weight column (e.g. ``"PWGTP"``).
    rep_weights
        List of replicate weight column names.
    scale
        Replicate weight scaling factor (default ``4/80 = 0.05`` for
        ACS 80 successive-difference replicate weights).
    """

    def __init__(
        self,
        df: pd.DataFrame,
        weight: str,
        rep_weights: list[str],
        scale: float = 4.0 / 80,
    ) -> None:
        self.df = df
        self.weight = weight
        self.rep_weights = rep_weights
        self.scale = scale

    def __repr__(self) -> str:
        return (
            f"SurveyDesign(n={len(self.df)}, weight={self.weight!r}, "
            f"rep_weights={len(self.rep_weights)})"
        )

    def weighted_estimate(self, variable: str) -> float:
        """Compute a weighted estimate (sum) for a variable."""
        return (self.df[variable] * self.df[self.weight]).sum()

    def weighted_mean(self, variable: str) -> float:
        """Compute a weighted mean for a variable."""
        total_weight = self.df[self.weight].sum()
        if total_weight == 0:
            return 0.0
        return (self.df[variable] * self.df[self.weight]).sum() / total_weight

    def standard_error(self, variable: str) -> float:
        """Compute the replicate-weight standard error for a weighted sum.

        Uses the successive-differences replication (SDR) formula:
        ``SE = sqrt(scale * sum((rep_est_r - full_est)^2))``
        """
        import numpy as np

        full_est = self.weighted_estimate(variable)
        sq_diffs = 0.0
        for rw in self.rep_weights:
            rep_est = (self.df[variable] * self.df[rw]).sum()
            sq_diffs += (rep_est - full_est) ** 2

        return float(np.sqrt(self.scale * sq_diffs))


def to_survey(
    df: pd.DataFrame,
    weight_type: str = "person",
    design: str = "rep_weights",
) -> SurveyDesign:
    """Convert a PUMS DataFrame to a weighted survey design object.

    Wraps the DataFrame with its weight and replicate weight columns,
    enabling weighted estimates and standard error computation using
    successive differences replication.

    Parameters
    ----------
    df
        PUMS DataFrame (from ``get_pums(rep_weights='person')``).
    weight_type
        Weight type: ``"person"`` (default) or ``"housing"``.
    design
        Survey design type. Only ``"rep_weights"`` is supported.

    Returns
    -------
    SurveyDesign
        A survey design object with methods for weighted estimation.

    Raises
    ------
    ValueError
        If required weight columns are missing from the DataFrame.
    """
    if design != "rep_weights":
        raise ValueError(f"Only 'rep_weights' design is supported, got {design!r}")

    if weight_type == "person":
        weight = "PWGTP"
        rep_weight_cols = [f"PWGTP{i}" for i in range(1, 81)]
    elif weight_type == "housing":
        weight = "WGTP"
        rep_weight_cols = [f"WGTP{i}" for i in range(1, 81)]
    else:
        raise ValueError(
            f"weight_type must be 'person' or 'housing', got {weight_type!r}"
        )

    if weight not in df.columns:
        raise ValueError(
            f"Weight column {weight!r} not found in DataFrame. "
            f"Did you call get_pums(rep_weights='{weight_type}')?"
        )

    # Only include replicate weight columns that exist.
    available_rw = [c for c in rep_weight_cols if c in df.columns]
    if not available_rw:
        raise ValueError(
            f"No replicate weight columns found (e.g. {rep_weight_cols[0]!r}). "
            f"Did you call get_pums(rep_weights='{type}')?"
        )

    return SurveyDesign(
        df=df,
        weight=weight,
        rep_weights=available_rw,
    )
