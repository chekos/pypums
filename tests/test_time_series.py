"""Tests for ``time_series`` parameter in ``get_estimates()``."""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_estimates

pytestmark = pytest.mark.phase3


def test_time_series_adds_date_columns(fake_api_key):
    """time_series=True should include DATE_CODE and DATE_DESC columns."""
    multi_date = [
        ["NAME", "POP_2023", "state", "DATE_CODE", "DATE_DESC"],
        ["California", "38965193", "06", "1", "4/1/2020 population estimate"],
        ["California", "39000000", "06", "2", "7/1/2020 population estimate"],
        ["Texas", "30503301", "48", "1", "4/1/2020 population estimate"],
        ["Texas", "30600000", "48", "2", "7/1/2020 population estimate"],
    ]
    with patch("pypums.estimates._call_census_api", return_value=multi_date):
        df = get_estimates(
            geography="state",
            product="population",
            variables=["POP_2023"],
            time_series=True,
            key=fake_api_key,
        )
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 2  # Multiple date rows


def test_time_series_false_no_date_params(estimates_api_response, fake_api_key):
    """time_series=False should not add DATE_CODE to API params."""
    with patch(
        "pypums.estimates._call_census_api", return_value=estimates_api_response
    ) as mock_call:
        get_estimates(
            geography="state",
            product="population",
            time_series=False,
            key=fake_api_key,
        )
    params = mock_call.call_args[0][1]
    assert "DATE_CODE" not in params


def test_time_series_true_adds_date_params(estimates_api_response, fake_api_key):
    """time_series=True should add DATE_CODE='*' to API params."""
    with patch(
        "pypums.estimates._call_census_api", return_value=estimates_api_response
    ) as mock_call:
        get_estimates(
            geography="state",
            product="population",
            time_series=True,
            key=fake_api_key,
        )
    params = mock_call.call_args[0][1]
    assert params.get("DATE_CODE") == "*"
