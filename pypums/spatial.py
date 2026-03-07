"""Spatial/geometry support for Census data.

Provides TIGER/Line shapefile fetching and merging, plus
dot-density conversion for thematic mapping.

Requires ``geopandas`` (optional dependency).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd

# TIGER/Line cartographic boundary base URL.
_TIGER_BASE = "https://www2.census.gov/geo/tiger"

# Mapping of pypums geography names to TIGER/Line shapefile identifiers.
_GEO_TO_TIGER: dict[str, str] = {
    "state": "cb_{year}_us_state_{resolution}",
    "county": "cb_{year}_us_county_{resolution}",
    "tract": "cb_{year}_{state_fips}_tract_{resolution}",
    "block group": "cb_{year}_{state_fips}_bg_{resolution}",
    "place": "cb_{year}_{state_fips}_place_{resolution}",
    "congressional district": "cb_{year}_us_cd{congress}_{resolution}",
    "zcta": "cb_{year}_us_zcta520_{resolution}",
    "puma": "cb_{year}_{state_fips}_puma20_{resolution}",
    "cbsa": "cb_{year}_us_cbsa_{resolution}",
    "csa": "cb_{year}_us_csa_{resolution}",
}


def _fetch_tiger_shapes(
    geography: str,
    *,
    state: str | None = None,
    year: int = 2023,
    resolution: str = "500k",
) -> gpd.GeoDataFrame:
    """Download TIGER/Line cartographic boundary shapefiles.

    Parameters
    ----------
    geography
        Geography level name.
    state
        State FIPS code (required for sub-state geographies).
    year
        Data year for the shapefiles.
    resolution
        Resolution: ``"500k"``, ``"5m"``, or ``"20m"``.

    Returns
    -------
    gpd.GeoDataFrame
        Shapefile geometries with a ``GEOID`` column.
    """
    import geopandas as _gpd

    geo = geography.lower()

    # Build the shapefile URL.
    template = _GEO_TO_TIGER.get(geo)
    if template is None:
        raise ValueError(
            f"No TIGER/Line shapefile mapping for geography: {geography!r}"
        )

    # Resolve state FIPS if needed.
    state_fips = state or "us"
    if state and not state.isdigit():
        from pypums.api.geography import _resolve_state_fips

        state_fips = _resolve_state_fips(state)

    # Congress number changes every 2 years starting from the 113th (2013).
    congress = str(113 + (year - 2013) // 2) if year >= 2013 else "113"

    filename = template.format(
        year=year,
        state_fips=state_fips,
        resolution=resolution,
        congress=congress,
    )

    url = f"{_TIGER_BASE}/GENZ{year}/shp/{filename}.zip"

    return _gpd.read_file(url)


def attach_geometry(
    df: pd.DataFrame,
    geography: str,
    *,
    state: str | None = None,
    year: int = 2023,
    resolution: str = "500k",
) -> gpd.GeoDataFrame:
    """Fetch TIGER/Line shapes and merge with Census tabular data.

    Parameters
    ----------
    df
        Census data DataFrame with a ``GEOID`` column.
    geography
        Geography level name.
    state
        State FIPS code or abbreviation.
    year
        Data year.
    resolution
        Shapefile resolution.

    Returns
    -------
    gpd.GeoDataFrame
        Merged GeoDataFrame with Census data and geometry.
    """
    import geopandas as _gpd

    shapes = _fetch_tiger_shapes(
        geography,
        state=state,
        year=year,
        resolution=resolution,
    )

    if "GEOID" not in df.columns:
        raise ValueError(
            "DataFrame has no GEOID column. geometry=True requires a "
            "geography level that produces GEOID (e.g. 'state', 'county')."
        )

    # Merge on GEOID.
    merged = shapes[["GEOID", "geometry"]].merge(df, on="GEOID", how="right")

    return _gpd.GeoDataFrame(merged, geometry="geometry", crs=shapes.crs)


def as_dot_density(
    gdf: gpd.GeoDataFrame,
    values: dict[str, str],
    *,
    dots_per_value: int = 100,
    seed: int | None = None,
) -> gpd.GeoDataFrame:
    """Convert polygon GeoDataFrame to dot-density points.

    For each polygon, generates random points proportional to the value
    in each specified column.

    Parameters
    ----------
    gdf
        Input GeoDataFrame with polygon geometries.
    values
        Mapping of ``{column_name: label}`` for columns to convert.
    dots_per_value
        Number of data units per dot (default 100).
    seed
        Random seed for reproducibility.

    Returns
    -------
    gpd.GeoDataFrame
        Point GeoDataFrame with one row per dot.
    """
    import geopandas as _gpd
    import numpy as np
    from shapely.geometry import Point

    rng = np.random.default_rng(seed)

    rows = []
    for _, feature in gdf.iterrows():
        polygon = feature.geometry
        if polygon is None or polygon.is_empty:
            continue

        minx, miny, maxx, maxy = polygon.bounds

        for col, label in values.items():
            count = int(feature[col])
            n_dots = max(count // dots_per_value, 0)

            dots_placed = 0
            attempts = 0
            max_attempts = max(n_dots * 200, 1000)
            while dots_placed < n_dots and attempts < max_attempts:
                # Generate candidate points within the bounding box.
                batch = max(n_dots - dots_placed, 10)
                xs = rng.uniform(minx, maxx, size=batch)
                ys = rng.uniform(miny, maxy, size=batch)
                attempts += batch

                for x, y in zip(xs, ys, strict=True):
                    pt = Point(x, y)
                    if polygon.contains(pt):
                        rows.append(
                            {
                                "geometry": pt,
                                "value": label,
                            }
                        )
                        dots_placed += 1
                        if dots_placed >= n_dots:
                            break

    return _gpd.GeoDataFrame(rows, geometry="geometry", crs=gdf.crs)
