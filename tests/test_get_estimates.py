"""Tests for ``get_estimates()`` — Population Estimates Program data.

Phase 3 — Estimates, Flows, Survey.

These tests define the contract for ``get_estimates()``:

* Returns a DataFrame.
* ``product`` parameter selects population/components/housing/characteristics.
* ``breakdown`` splits characteristics by AGEGROUP, RACE, SEX, HISP.
* ``time_series=True`` returns data across multiple years.
* ``output="tidy"`` melts value columns into long format.
* ``output="wide"`` keeps one row per geography (default pre-Phase 4 behavior).
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_estimates

pytestmark = pytest.mark.phase3


def _mock_get_estimates(estimates_api_response):
    return patch(
        "pypums.estimates._call_census_api",
        return_value=estimates_api_response,
    )


class TestGetEstimatesReturnType:
    def test_returns_dataframe(self, estimates_api_response, fake_api_key):
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="population",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestGetEstimatesProducts:
    def test_population_product(self, estimates_api_response, fake_api_key):
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="population",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)

    def test_components_product(self, estimates_api_response, fake_api_key):
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="components",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)

    def test_housing_product(self, estimates_api_response, fake_api_key):
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="housing",
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)


class TestGetEstimatesBreakdown:
    def test_breakdown_parameter(self, estimates_api_response, fake_api_key):
        """breakdown splits characteristics by demographic dimensions."""
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="characteristics",
                breakdown=["AGEGROUP", "SEX"],
                breakdown_labels=True,
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)


class TestGetEstimatesTimeSeries:
    def test_time_series(self, estimates_api_response, fake_api_key):
        """time_series=True should return data across multiple years."""
        # Mock a multi-year response
        multi_year = [
            ["NAME", "POP_2022", "POP_2023", "state"],
            ["California", "38940000", "38965193", "06"],
            ["Texas", "30030000", "30503301", "48"],
        ]
        with patch("pypums.estimates._call_census_api", return_value=multi_year):
            df = get_estimates(
                geography="state",
                product="population",
                time_series=True,
                key=fake_api_key,
            )
        assert isinstance(df, pd.DataFrame)


class TestGetEstimatesOutput:
    """Test output format parameter."""

    def test_tidy_output_has_variable_and_value(
        self, estimates_api_response, fake_api_key
    ):
        """Tidy output should have 'variable' and 'value' columns."""
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="population",
                variables=["POP_2023", "DENSITY_2023"],
                output="tidy",
                key=fake_api_key,
            )
        assert "variable" in df.columns
        assert "value" in df.columns

    def test_tidy_output_has_more_rows_than_wide(
        self, estimates_api_response, fake_api_key
    ):
        """Tidy format melts variables so there are more rows."""
        with _mock_get_estimates(estimates_api_response):
            df_tidy = get_estimates(
                geography="state",
                product="population",
                variables=["POP_2023", "DENSITY_2023"],
                output="tidy",
                key=fake_api_key,
            )
        with _mock_get_estimates(estimates_api_response):
            df_wide = get_estimates(
                geography="state",
                product="population",
                variables=["POP_2023", "DENSITY_2023"],
                output="wide",
                key=fake_api_key,
            )
        assert len(df_tidy) > len(df_wide)

    def test_wide_output_keeps_columns(self, estimates_api_response, fake_api_key):
        """Wide output keeps variable columns intact."""
        with _mock_get_estimates(estimates_api_response):
            df = get_estimates(
                geography="state",
                product="population",
                variables=["POP_2023", "DENSITY_2023"],
                output="wide",
                key=fake_api_key,
            )
        assert "POP_2023" in df.columns
        assert "DENSITY_2023" in df.columns

    def test_invalid_output_raises(self, fake_api_key):
        """Invalid output value should raise ValueError."""
        with pytest.raises(ValueError, match="output must be"):
            get_estimates(
                geography="state",
                product="population",
                output="invalid",
                key=fake_api_key,
            )
