"""Tests for ``get_flows()`` — ACS Migration Flows data.

Phase 3 — Estimates, Flows, Survey.

These tests define the contract for ``get_flows()``:

* Returns a DataFrame.
* Output includes MOVEDIN, MOVEDOUT, MOVEDNET columns.
* County-to-county flows work when geography + state + county are given.
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
    def test_has_flow_columns(self, flows_api_response, fake_api_key):
        """Output must include the three core migration flow columns."""
        with _mock_get_flows(flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
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
