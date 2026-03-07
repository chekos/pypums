"""Tests for ``get_estimates()`` — Population Estimates Program data.

Phase 3 — Estimates, Flows, Survey.

These tests define the contract for ``get_estimates()``:

* Returns a DataFrame.
* ``product`` parameter selects population/components/housing/characteristics.
* ``breakdown`` splits characteristics by AGEGROUP, RACE, SEX, HISP.
* ``time_series=True`` returns multiple years of data.
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
