"""Tests for geography hierarchy definitions and validation.

Phase 0 — Foundation.

These tests define the contract for the geography module:
* All 25+ Census geography names are accepted.
* Geographies that require parent geographies (e.g. county → state) raise
  when those parents are not supplied.
* ``build_geography_query`` returns the correct Census API ``for`` / ``in``
  parameter strings.
"""

import pytest

from pypums.api.geography import GEOGRAPHY_HIERARCHY, build_geography_query

pytestmark = pytest.mark.phase0


# The minimum set of geographies tidycensus supports — pypums must too.
EXPECTED_GEOGRAPHIES = [
    "us",
    "region",
    "division",
    "state",
    "county",
    "county subdivision",
    "tract",
    "block group",
    "block",
    "place",
    "congressional district",
    "state legislative district (upper)",
    "state legislative district (lower)",
    "zcta",
    "school district (unified)",
    "school district (elementary)",
    "school district (secondary)",
    "cbsa",
    "csa",
    "puma",
    "american indian area/alaska native area/hawaiian home land",
]


@pytest.mark.parametrize("geo", EXPECTED_GEOGRAPHIES)
def test_valid_geography_names(geo):
    """Every expected geography string is present in the hierarchy mapping."""
    assert geo in GEOGRAPHY_HIERARCHY


def test_county_requires_state():
    """Requesting county-level data without a state should raise."""
    with pytest.raises(ValueError, match="(?i)state"):
        build_geography_query("county")


def test_tract_requires_state_and_county():
    """Requesting tract-level data without state+county should raise."""
    with pytest.raises(ValueError):
        build_geography_query("tract", state="06")  # missing county


def test_build_geography_query_state():
    """State-level query needs no 'in' clause."""
    for_clause, in_clause = build_geography_query("state")
    assert "state" in for_clause
    assert in_clause is None


def test_build_geography_query_county_in_state():
    """County-level query returns a 'for' and an 'in' clause."""
    for_clause, in_clause = build_geography_query("county", state="06")
    assert "county" in for_clause
    assert in_clause is not None
    assert "state:06" in in_clause
