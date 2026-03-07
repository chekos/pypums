"""Tests for ``load_variables()`` — Census variable discovery.

Phase 1 — Core Data Functions.

These tests define the contract for ``load_variables()``:

* Returns a DataFrame with name, label, concept columns.
* Works for ACS and Decennial dataset identifiers.
* ``cache=True`` stores the result locally so repeated calls are fast.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import load_variables

pytestmark = pytest.mark.phase1


def _mock_load_variables(variables_api_response):
    return patch(
        "pypums.variables._fetch_variables_json",
        return_value=variables_api_response,
    )


class TestLoadVariablesReturnType:
    def test_returns_dataframe(self, variables_api_response, fake_api_key):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2023, dataset="acs5")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestLoadVariablesColumns:
    def test_has_expected_columns(self, variables_api_response, fake_api_key):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2023, dataset="acs5")
        for col in ("name", "label", "concept"):
            assert col in df.columns, f"Missing column: {col}"


class TestLoadVariablesDatasets:
    """load_variables() must accept both ACS and Decennial dataset strings."""

    def test_acs5(self, variables_api_response):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2023, dataset="acs5")
        assert isinstance(df, pd.DataFrame)

    def test_acs1(self, variables_api_response):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2023, dataset="acs1")
        assert isinstance(df, pd.DataFrame)

    def test_decennial_pl(self, variables_api_response):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2020, dataset="pl")
        assert isinstance(df, pd.DataFrame)

    def test_acs5_subject(self, variables_api_response):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2023, dataset="acs5/subject")
        assert isinstance(df, pd.DataFrame)

    def test_acs5_profile(self, variables_api_response):
        with _mock_load_variables(variables_api_response):
            df = load_variables(year=2023, dataset="acs5/profile")
        assert isinstance(df, pd.DataFrame)


class TestLoadVariablesCache:
    """``cache=True`` should store results locally for reuse."""

    def test_cache_stores_locally(self, variables_api_response, cache_dir):
        with _mock_load_variables(variables_api_response):
            # First call fetches from API
            df1 = load_variables(year=2023, dataset="acs5", cache=True)

        # Second call should work without the mock (reading from cache)
        # This will fail until caching is implemented — that's the point.
        df2 = load_variables(year=2023, dataset="acs5", cache=True)
        pd.testing.assert_frame_equal(df1, df2)
