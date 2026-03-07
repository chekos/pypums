"""Tests for ``get_pums()`` — PUMS microdata via Census API.

Phase 2 — MOE + Spatial + Enhanced PUMS.

These tests define the contract for the API-based ``get_pums()``:

* Returns a DataFrame of individual-level microdata records.
* ``variables_filter`` reduces the returned rows (server-side filtering).
* ``recode=True`` adds ``*_label`` columns with human-readable values.
* ``rep_weights`` includes replicate weight columns.
* State is required (raises without it).
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_pums

pytestmark = pytest.mark.phase2


def _mock_get_pums(pums_api_response):
    return patch(
        "pypums.pums._call_census_api",
        return_value=pums_api_response,
    )


class TestGetPumsReturnType:
    def test_returns_dataframe(self, pums_api_response, fake_api_key):
        with _mock_get_pums(pums_api_response):
            df = get_pums(
                variables=["AGEP", "SEX"],
                state="CA",
                year=2023,
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetPumsVariablesFilter:
    def test_filter_reduces_rows(self, pums_api_response, fake_api_key):
        """variables_filter should cause the API to return fewer rows."""
        # Without filter
        with _mock_get_pums(pums_api_response):
            df_all = get_pums(
                variables=["AGEP", "SEX"],
                state="CA",
                key=fake_api_key,
            )

        # With filter — mock returns same data but get_pums should pass
        # the filter to the API call; we verify it doesn't crash and
        # the parameter is accepted.
        filtered_response = [
            pums_api_response[0],  # header
            pums_api_response[1],  # only one matching row
        ]
        with patch("pypums.pums._call_census_api", return_value=filtered_response):
            df_filtered = get_pums(
                variables=["AGEP", "SEX"],
                state="CA",
                variables_filter={"SEX": 1},
                key=fake_api_key,
            )

        assert len(df_filtered) < len(df_all)


class TestGetPumsRecode:
    def test_recode_adds_label_columns(self, pums_api_response, fake_api_key):
        """``recode=True`` should add *_label columns for coded variables."""
        with _mock_get_pums(pums_api_response):
            df = get_pums(
                variables=["AGEP", "SEX"],
                state="CA",
                recode=True,
                key=fake_api_key,
            )
        # SEX is a coded variable (1=Male, 2=Female) — should get a label col
        assert "SEX_label" in df.columns


class TestGetPumsRepWeights:
    def test_rep_weights_person(self, pums_api_response, fake_api_key):
        """``rep_weights='person'`` should include PWGTP1..PWGTP80 columns."""
        # Mock a response that includes weight columns
        header = pums_api_response[0] + ["PWGTP1", "PWGTP2"]
        rows = [row + ["50", "48"] for row in pums_api_response[1:]]
        response_with_weights = [header] + rows

        with patch("pypums.pums._call_census_api", return_value=response_with_weights):
            df = get_pums(
                variables=["AGEP", "SEX"],
                state="CA",
                rep_weights="person",
                key=fake_api_key,
            )
        assert "PWGTP1" in df.columns


class TestGetPumsStateRequired:
    def test_state_required(self, fake_api_key):
        """get_pums() should raise when no state is provided."""
        with pytest.raises((ValueError, TypeError)):
            get_pums(
                variables=["AGEP", "SEX"],
                key=fake_api_key,
            )
