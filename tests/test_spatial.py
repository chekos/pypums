"""Tests for spatial / geometry support.

Phase 2 — MOE + Spatial + Enhanced PUMS.

These tests are skipped if ``geopandas`` is not installed.  They verify:

* ``geometry=True`` in ``get_acs()`` returns a GeoDataFrame.
* The returned GeoDataFrame has a valid CRS (EPSG:4269 / NAD83).
* ``as_dot_density()`` converts polygon geometries to point geometries.
"""

from unittest.mock import patch

import pytest

gpd = pytest.importorskip("geopandas", reason="geopandas required for spatial tests")

from pypums import get_acs  # noqa: E402
from pypums.spatial import as_dot_density  # noqa: E402

pytestmark = [pytest.mark.phase2, pytest.mark.spatial]


@pytest.fixture()
def mock_acs_with_geometry(acs_api_response_tidy):
    """Mock both the Census API call and the TIGER/Line shapefile fetch."""
    # We need to mock two things:
    # 1. The Census API call that returns tabular data
    # 2. The TIGER/Line shapefile download that returns geometries
    from shapely.geometry import box

    # Create minimal GeoDataFrame for mocking the geometry fetch
    mock_geo = gpd.GeoDataFrame(
        {
            "GEOID": ["06037", "06059"],
            "geometry": [
                box(-118.5, 33.7, -117.6, 34.3),
                box(-118.1, 33.4, -117.4, 33.9),
            ],
        },
        crs="EPSG:4269",
    )

    return (
        patch("pypums.acs._call_census_api", return_value=acs_api_response_tidy),
        patch("pypums.spatial._fetch_tiger_shapes", return_value=mock_geo),
    )


class TestGetAcsGeometry:
    def test_returns_geodataframe(self, mock_acs_with_geometry, fake_api_key):
        api_mock, geo_mock = mock_acs_with_geometry
        with api_mock, geo_mock:
            gdf = get_acs(
                geography="county",
                variables="B01001_001",
                state="CA",
                geometry=True,
                key=fake_api_key,
            )
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert "geometry" in gdf.columns

    def test_has_correct_crs(self, mock_acs_with_geometry, fake_api_key):
        api_mock, geo_mock = mock_acs_with_geometry
        with api_mock, geo_mock:
            gdf = get_acs(
                geography="county",
                variables="B01001_001",
                state="CA",
                geometry=True,
                key=fake_api_key,
            )
        assert gdf.crs is not None
        assert gdf.crs.to_epsg() == 4269


class TestAsDotDensity:
    def test_converts_polygons_to_points(self):
        from shapely.geometry import box

        gdf = gpd.GeoDataFrame(
            {
                "GEOID": ["06037"],
                "pop": [1000],
                "geometry": [box(-118.5, 33.7, -117.6, 34.3)],
            },
            crs="EPSG:4269",
        )

        result = as_dot_density(
            gdf,
            values={"pop": "Population"},
            dots_per_value=100,
            seed=42,
        )

        assert isinstance(result, gpd.GeoDataFrame)
        # 1000 people / 100 per dot = 10 dots
        assert len(result) == 10
        # All geometries should be points
        assert all(result.geometry.geom_type == "Point")
