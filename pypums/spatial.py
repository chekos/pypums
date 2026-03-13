"""Spatial/geometry support for Census data.

Provides shapefile fetching (via `pygris <https://github.com/walkerke/pygris>`_)
and merging, plus dot-density conversion and areal interpolation for thematic
mapping.

Requires the ``spatial`` optional dependency group (``geopandas`` + ``pygris``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    import geopandas as gpd
    import pandas as pd


def _pygris_func(name: str) -> Callable[..., Any]:
    """Lazily import a pygris function by name."""
    import pygris

    return getattr(pygris, name)


# Mapping of pypums geography names to (pygris_function_name, accepts_state).
_GEO_TO_PYGRIS: dict[str, tuple[str, bool]] = {
    "state": ("states", False),
    "county": ("counties", True),
    "tract": ("tracts", True),
    "block group": ("block_groups", True),
    "place": ("places", True),
    "congressional district": ("congressional_districts", False),
    "zcta": ("zctas", False),
    "puma": ("pumas", True),
    "cbsa": ("core_based_statistical_areas", False),
    "csa": ("combined_statistical_areas", False),
}


def _normalize_geoid(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Ensure the GeoDataFrame has a ``GEOID`` column.

    pygris may return ``GEOID20``, ``GEOID10``, or ``AFFGEOID`` depending
    on the geography and vintage year.  This normalizes to ``GEOID``.
    """
    if "GEOID" in gdf.columns:
        return gdf

    for candidate in ("GEOID20", "GEOID10", "AFFGEOID"):
        if candidate in gdf.columns:
            return gdf.rename(columns={candidate: "GEOID"})

    msg = (
        "pygris returned a GeoDataFrame without a GEOID column. "
        f"Available columns: {list(gdf.columns)}"
    )
    raise ValueError(msg)


def _fetch_tiger_shapes(
    geography: str,
    *,
    state: str | None = None,
    year: int = 2023,
    resolution: str = "500k",
) -> gpd.GeoDataFrame:
    """Download cartographic boundary shapefiles via pygris.

    Parameters
    ----------
    geography
        Geography level name.
    state
        State FIPS code, abbreviation, or name (required for sub-state
        geographies).
    year
        Data year for the shapefiles.
    resolution
        Resolution: ``"500k"``, ``"5m"``, or ``"20m"``.

    Returns
    -------
    gpd.GeoDataFrame
        Shapefile geometries with a ``GEOID`` column in EPSG:4269.
    """
    geo = geography.lower()

    entry = _GEO_TO_PYGRIS.get(geo)
    if entry is None:
        raise ValueError(f"No shapefile mapping for geography: {geography!r}")

    func_name, accepts_state = entry
    func = _pygris_func(func_name)

    kwargs: dict[str, Any] = {
        "cb": True,
        "resolution": resolution,
        "year": year,
        "cache": True,
    }
    if accepts_state and state is not None:
        kwargs["state"] = state

    gdf = func(**kwargs)

    # Normalize GEOID column name across vintages.
    gdf = _normalize_geoid(gdf)

    # Guarantee EPSG:4269 (NAD83) as documented.
    if gdf.crs is None or gdf.crs.to_epsg() != 4269:
        gdf = gdf.to_crs(epsg=4269)

    return gdf


def attach_geometry(
    df: pd.DataFrame,
    geography: str,
    *,
    state: str | None = None,
    year: int = 2023,
    resolution: str = "500k",
) -> gpd.GeoDataFrame:
    """Fetch shapes via pygris and merge with Census tabular data.

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


def interpolate_pw(
    from_gdf: gpd.GeoDataFrame,
    to_gdf: gpd.GeoDataFrame,
    *,
    value_col: str,
    weight_col: str = "POP",
    extensive: bool = True,
) -> gpd.GeoDataFrame:
    """Population-weighted areal interpolation.

    Transfers values from one set of polygons (``from_gdf``) to
    another (``to_gdf``) using population weights from a third
    layer (the weight column in ``from_gdf``).

    This is a simplified implementation that uses overlay intersection
    areas weighted by population counts.

    Parameters
    ----------
    from_gdf
        Source GeoDataFrame with the values to interpolate.
    to_gdf
        Target GeoDataFrame defining the output zones.
    value_col
        Column in *from_gdf* containing the value to interpolate.
    weight_col
        Column in *from_gdf* containing population weights (default ``"POP"``).
    extensive
        If True (default), treat as an extensive variable (sum).
        If False, treat as an intensive variable (weighted average).

    Returns
    -------
    gpd.GeoDataFrame
        Copy of *to_gdf* with an interpolated value column added.
    """
    import geopandas as _gpd

    # Ensure both GeoDataFrames use the same CRS.
    if from_gdf.crs != to_gdf.crs:
        from_gdf = from_gdf.to_crs(to_gdf.crs)

    # Add unique IDs for tracking.
    from_copy = from_gdf[[value_col, weight_col, "geometry"]].copy()
    from_copy["_from_idx"] = range(len(from_copy))
    to_copy = to_gdf.copy()
    to_copy["_to_idx"] = range(len(to_copy))

    # Compute overlay intersection.
    overlay = _gpd.overlay(
        from_copy,
        to_copy[["_to_idx", "geometry"]],
        how="intersection",
    )

    if overlay.empty:
        result = to_gdf.copy()
        result[value_col] = 0.0
        return result

    # Compute intersection areas.
    overlay["_int_area"] = overlay.geometry.area

    # Compute weighted population in each intersection piece.
    # Weight each intersection proportionally by its area share of the
    # source zone.
    from_areas = from_copy.geometry.area
    overlay["_from_area"] = overlay["_from_idx"].map(
        dict(zip(from_copy["_from_idx"], from_areas, strict=True))
    )
    overlay["_area_share"] = overlay["_int_area"] / overlay["_from_area"]
    overlay["_int_weight"] = overlay[weight_col] * overlay["_area_share"]

    # Compute total weight going to each target zone.
    target_weights = overlay.groupby("_to_idx")["_int_weight"].sum()

    if extensive:
        # Extensive: distribute the total value proportionally.
        overlay["_weighted_value"] = overlay[value_col] * overlay["_area_share"]
        target_values = overlay.groupby("_to_idx")["_weighted_value"].sum()
    else:
        # Intensive: population-weighted average.
        overlay["_wv"] = overlay[value_col] * overlay["_int_weight"]
        target_wv = overlay.groupby("_to_idx")["_wv"].sum()
        target_values = target_wv / target_weights.replace(0, float("nan"))

    result = to_gdf.copy().reset_index(drop=True)
    result[value_col] = result.index.map(
        dict(zip(target_values.index, target_values.values, strict=True))
    ).fillna(0.0)

    return result
