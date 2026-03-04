"""Tests for ``get_acs()`` — American Community Survey data retrieval.

Phase 1 — Core Data Functions.

These tests mock the Census API so no network calls are made.  They define
the contract for ``get_acs()``:

* Returns a pandas DataFrame (or GeoDataFrame when ``geometry=True``).
* Tidy output has columns: GEOID, NAME, variable, estimate, moe.
* Wide output pivots variables into separate columns.
* Accepts a single variable string or a list of variables.
* ``table`` parameter fetches all variables in a table.
* ``moe_level`` scales margins of error to 95 % or 99 % confidence.
* ``summary_var`` adds a denominator column for proportion calculations.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_acs

pytestmark = pytest.mark.phase1


# ---------------------------------------------------------------------------
# Helper to build the mock — all tests patch the same internal API call.
# ---------------------------------------------------------------------------
def _mock_get_acs(acs_api_response_tidy, **overrides):
    """Return a context-manager that patches the Census API client."""
    return patch(
        "pypums.acs._call_census_api",
        return_value=acs_api_response_tidy,
    )


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------

class TestGetAcsReturnType:
    """get_acs() must always return a DataFrame."""

    def test_returns_dataframe(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables="B01001_001",
                state="CA",
                year=2023,
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetAcsTidyFormat:
    """Default tidy output: one row per geography × variable."""

    def test_tidy_columns(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                key=fake_api_key,
            )
        for col in ("GEOID", "NAME", "variable", "estimate", "moe"):
            assert col in df.columns, f"Missing column: {col}"

    def test_tidy_variable_column_values(self, acs_api_response_tidy, fake_api_key):
        """The 'variable' column should contain the requested variable IDs."""
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                key=fake_api_key,
            )
        assert set(df["variable"].unique()) == {"B01001_001", "B02001_002"}


class TestGetAcsWideFormat:
    """Wide output: one row per geography, variables as columns."""

    def test_wide_columns(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                output="wide",
                key=fake_api_key,
            )
        assert "GEOID" in df.columns
        assert "NAME" in df.columns
        # Wide format should have estimate and MOE columns per variable
        assert "B01001_001E" in df.columns
        assert "B01001_001M" in df.columns
        assert "B02001_002E" in df.columns
        assert "B02001_002M" in df.columns


class TestGetAcsVariableInput:
    """get_acs() should accept both a single string and a list."""

    def test_single_variable_string(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables="B01001_001",
                state="CA",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)

    def test_multiple_variables_list(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables=["B01001_001", "B02001_002"],
                state="CA",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)


class TestGetAcsTable:
    """The ``table`` parameter fetches all variables in a Census table."""

    def test_table_parameter(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                table="B01001",
                state="CA",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetAcsMoeLevel:
    """MOE should be scaled when ``moe_level`` is 95 or 99."""

    def test_moe_level_scaling(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df_90 = get_acs(
                geography="county",
                variables="B01001_001",
                state="CA",
                moe_level=90,
                key=fake_api_key,
            )
        with _mock_get_acs(acs_api_response_tidy):
            df_99 = get_acs(
                geography="county",
                variables="B01001_001",
                state="CA",
                moe_level=99,
                key=fake_api_key,
            )
        # 99 % MOE should be larger than 90 % MOE for the same estimates
        # (scaling factor: 1.645 → 2.576)
        if df_90["moe"].iloc[0] != 0:
            assert df_99["moe"].iloc[0] > df_90["moe"].iloc[0]


class TestGetAcsSummaryVar:
    """``summary_var`` adds a denominator column for proportion work."""

    def test_summary_var_in_output(self, acs_api_response_tidy, fake_api_key):
        with _mock_get_acs(acs_api_response_tidy):
            df = get_acs(
                geography="county",
                variables="B02001_002",
                summary_var="B01001_001",
                state="CA",
                key=fake_api_key,
            )
        assert "summary_est" in df.columns
        assert "summary_moe" in df.columns
