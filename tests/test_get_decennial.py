"""Tests for ``get_decennial()`` — Decennial Census data retrieval.

Phase 1 — Core Data Functions.

These tests mock the Census API and define the contract for
``get_decennial()``:

* Returns a DataFrame with GEOID, NAME, variable, value (tidy).
* Wide output pivots variables into columns.
* Default summary file varies by year (sf1 for 2010, dhc for 2020).
* ``pop_group`` parameter works for DHC-A data.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_decennial

pytestmark = pytest.mark.phase1


def _mock_get_decennial(decennial_api_response):
    return patch(
        "pypums.decennial._call_census_api",
        return_value=decennial_api_response,
    )


class TestGetDecennialReturnType:

    def test_returns_dataframe(self, decennial_api_response, fake_api_key):
        with _mock_get_decennial(decennial_api_response):
            df = get_decennial(
                geography="state",
                variables="P1_001N",
                year=2020,
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetDecennialTidyFormat:

    def test_tidy_columns(self, decennial_api_response, fake_api_key):
        with _mock_get_decennial(decennial_api_response):
            df = get_decennial(
                geography="state",
                variables=["P1_001N", "P1_002N"],
                year=2020,
                key=fake_api_key,
            )
        for col in ("GEOID", "NAME", "variable", "value"):
            assert col in df.columns, f"Missing column: {col}"

    def test_no_moe_column(self, decennial_api_response, fake_api_key):
        """Decennial data is a full enumeration — no margin of error."""
        with _mock_get_decennial(decennial_api_response):
            df = get_decennial(
                geography="state",
                variables="P1_001N",
                year=2020,
                key=fake_api_key,
            )
        assert "moe" not in df.columns


class TestGetDecennialWideFormat:

    def test_wide_columns(self, decennial_api_response, fake_api_key):
        with _mock_get_decennial(decennial_api_response):
            df = get_decennial(
                geography="state",
                variables=["P1_001N", "P1_002N"],
                year=2020,
                output="wide",
                key=fake_api_key,
            )
        assert "GEOID" in df.columns
        assert "P1_001N" in df.columns
        assert "P1_002N" in df.columns


class TestGetDecennialSumfileDefaults:
    """The default summary file should depend on the census year."""

    def test_year_2020_defaults_to_dhc(self, decennial_api_response, fake_api_key):
        with _mock_get_decennial(decennial_api_response) as mock_call:
            get_decennial(
                geography="state",
                variables="P1_001N",
                year=2020,
                key=fake_api_key,
            )
        # The internal API call should reference the DHC dataset
        url_called = mock_call.call_args[0][0]
        assert "dec/dhc" in url_called

    def test_year_2010_defaults_to_sf1(self, decennial_api_response, fake_api_key):
        with _mock_get_decennial(decennial_api_response) as mock_call:
            get_decennial(
                geography="state",
                variables="P001001",
                year=2010,
                key=fake_api_key,
            )
        url_called = mock_call.call_args[0][0]
        assert "dec/sf1" in url_called


class TestGetDecennialPopGroup:
    """``pop_group`` parameter is used for DHC-A disaggregated data."""

    def test_pop_group_parameter(self, decennial_api_response, fake_api_key):
        with _mock_get_decennial(decennial_api_response):
            df = get_decennial(
                geography="state",
                variables="P1_001N",
                year=2020,
                pop_group="0001",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
