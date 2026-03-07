"""Tests for ``get_flows()`` — ACS Migration Flows data.

Phase 3 — Estimates, Flows, Survey.

These tests define the contract for ``get_flows()``:

* Returns a DataFrame.
* Output includes MOVEDIN, MOVEDOUT, MOVEDNET columns.
* County-to-county flows work when geography + state + county are given.
* ``output="tidy"`` melts flow columns into long format with estimate/moe.
* ``moe_level`` scales margins of error to 95% or 99% confidence.
* ``geometry=True`` returns a GeoDataFrame.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_flows

pytestmark = pytest.mark.phase3


def _mock_get_flows(flows_api_response):
    return patch(
        "pypums.flows._call_census_api",
        return_value=flows_api_response,
    )


class TestGetFlowsReturnType:
    def test_returns_dataframe(self, flows_api_response, fake_api_key):
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetFlowsColumns:
    def test_wide_has_flow_columns(self, flows_api_response, fake_api_key):
        """Wide output must include the three core migration flow columns."""
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                output="wide",
                key=fake_api_key,
            )
        for col in ("MOVEDIN", "MOVEDOUT", "MOVEDNET"):
            assert col in df.columns, f"Missing column: {col}"

    def test_has_origin_destination_names(self, flows_api_response, fake_api_key):
        """Should include names for both origin and destination."""
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                key=fake_api_key,
            )
        assert "FULL1_NAME" in df.columns
        assert "FULL2_NAME" in df.columns


class TestGetFlowsCountyLevel:
    def test_county_to_county(self, flows_api_response, fake_api_key):
        """County-level flows require state + county specification."""
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                year=2019,
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetFlowsOutput:
    """Test output format parameter."""

    def test_tidy_output_has_variable_estimate_moe(
        self, flows_api_response, fake_api_key
    ):
        """Tidy output should have variable, estimate, and moe columns."""
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                output="tidy",
                key=fake_api_key,
            )
        assert "variable" in df.columns
        assert "estimate" in df.columns
        assert "moe" in df.columns

    def test_tidy_variable_values(self, flows_api_response, fake_api_key):
        """Tidy variable column should contain MOVEDIN, MOVEDOUT, MOVEDNET."""
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                output="tidy",
                key=fake_api_key,
            )
        assert set(df["variable"].unique()) == {"MOVEDIN", "MOVEDOUT", "MOVEDNET"}

    def test_tidy_has_more_rows_than_wide(self, flows_api_response, fake_api_key):
        """Tidy format should have more rows since it melts 3 flow columns."""
        with _mock_get_flows(flows_api_response):
            df_tidy = get_flows(
                geography="county",
                state="CA",
                county="037",
                output="tidy",
                key=fake_api_key,
            )
        with _mock_get_flows(flows_api_response):
            df_wide = get_flows(
                geography="county",
                state="CA",
                county="037",
                output="wide",
                key=fake_api_key,
            )
        assert len(df_tidy) > len(df_wide)

    def test_invalid_output_raises(self, fake_api_key):
        """Invalid output value should raise ValueError."""
        with pytest.raises(ValueError, match="output must be"):
            get_flows(
                geography="county",
                output="invalid",
                key=fake_api_key,
            )


class TestGetFlowsMoeLevel:
    """MOE should be scaled when ``moe_level`` is 95 or 99."""

    def test_moe_99_larger_than_90(self, flows_api_response, fake_api_key):
        """99% MOE should be larger than 90% MOE."""
        with _mock_get_flows(flows_api_response):
            df_90 = get_flows(
                geography="county",
                state="CA",
                county="037",
                moe_level=90,
                output="wide",
                key=fake_api_key,
            )
        with _mock_get_flows(flows_api_response):
            df_99 = get_flows(
                geography="county",
                state="CA",
                county="037",
                moe_level=99,
                output="wide",
                key=fake_api_key,
            )
        # The MOVEDIN_M at 99% should be larger than at 90%.
        assert df_99["MOVEDIN_M"].iloc[0] > df_90["MOVEDIN_M"].iloc[0]

    def test_moe_95_scaling(self, flows_api_response, fake_api_key):
        """95% MOE should be between 90% and 99%."""
        with _mock_get_flows(flows_api_response):
            df_90 = get_flows(
                geography="county",
                state="CA",
                county="037",
                moe_level=90,
                output="wide",
                key=fake_api_key,
            )
        with _mock_get_flows(flows_api_response):
            df_95 = get_flows(
                geography="county",
                state="CA",
                county="037",
                moe_level=95,
                output="wide",
                key=fake_api_key,
            )
        assert df_95["MOVEDIN_M"].iloc[0] > df_90["MOVEDIN_M"].iloc[0]

    def test_invalid_moe_level_raises(self, fake_api_key):
        """Invalid moe_level should raise ValueError."""
        with pytest.raises(ValueError, match="moe_level must be"):
            get_flows(
                geography="county",
                moe_level=80,
                key=fake_api_key,
            )


class TestGetFlowsGeoid:
    """Flows should build a GEOID from origin FIPS columns."""

    def test_geoid_from_origin(self, flows_api_response, fake_api_key):
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                output="wide",
                key=fake_api_key,
            )
        assert "GEOID" in df.columns
        # GEOID should be state1 + county1 = "06" + "037" = "06037"
        assert df["GEOID"].iloc[0] == "06037"
