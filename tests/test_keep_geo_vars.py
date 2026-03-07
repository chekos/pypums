"""Tests for ``keep_geo_vars`` in get_acs() and get_decennial()."""

from unittest.mock import patch

import pytest

from pypums import get_acs, get_decennial

pytestmark = pytest.mark.phase1


class TestAcsKeepGeoVars:
    """Tests for keep_geo_vars in get_acs()."""

    def test_keep_geo_vars_true_preserves_fips(
        self, acs_api_response_tidy, fake_api_key
    ):
        """keep_geo_vars=True should keep state and county columns."""
        with patch("pypums.acs._call_census_api", return_value=acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                keep_geo_vars=True,
                key=fake_api_key,
            )
        assert "state" in df.columns
        assert "county" in df.columns

    def test_keep_geo_vars_false_drops_fips(self, acs_api_response_tidy, fake_api_key):
        """keep_geo_vars=False (default) should not include raw FIPS columns."""
        with patch("pypums.acs._call_census_api", return_value=acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                keep_geo_vars=False,
                key=fake_api_key,
            )
        assert "state" not in df.columns
        assert "county" not in df.columns

    def test_keep_geo_vars_wide_output(self, acs_api_response_tidy, fake_api_key):
        """keep_geo_vars=True should work with wide output too."""
        with patch("pypums.acs._call_census_api", return_value=acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                output="wide",
                keep_geo_vars=True,
                key=fake_api_key,
            )
        assert "state" in df.columns
        assert "county" in df.columns
        assert "GEOID" in df.columns


class TestDecennialKeepGeoVars:
    """Tests for keep_geo_vars in get_decennial()."""

    def test_keep_geo_vars_true_preserves_fips(
        self, decennial_api_response, fake_api_key
    ):
        """keep_geo_vars=True should keep state column."""
        with patch(
            "pypums.decennial._call_census_api", return_value=decennial_api_response
        ):
            df = get_decennial(
                geography="state",
                variables=["P1_001N", "P1_002N"],
                year=2020,
                keep_geo_vars=True,
                key=fake_api_key,
            )
        assert "state" in df.columns

    def test_keep_geo_vars_false_drops_fips(self, decennial_api_response, fake_api_key):
        """keep_geo_vars=False (default) should not include raw FIPS columns."""
        with patch(
            "pypums.decennial._call_census_api", return_value=decennial_api_response
        ):
            df = get_decennial(
                geography="state",
                variables=["P1_001N", "P1_002N"],
                year=2020,
                keep_geo_vars=False,
                key=fake_api_key,
            )
        assert "state" not in df.columns

    def test_keep_geo_vars_wide_output(self, decennial_api_response, fake_api_key):
        """keep_geo_vars=True should work with wide output."""
        with patch(
            "pypums.decennial._call_census_api", return_value=decennial_api_response
        ):
            df = get_decennial(
                geography="state",
                variables=["P1_001N", "P1_002N"],
                year=2020,
                output="wide",
                keep_geo_vars=True,
                key=fake_api_key,
            )
        assert "state" in df.columns
        assert "GEOID" in df.columns
