"""Tests for ``summary_files()`` and ``get_pop_groups()``."""

from unittest.mock import patch

import pandas as pd

from pypums import get_pop_groups, summary_files


class TestSummaryFiles:
    """Tests for summary_files()."""

    def test_returns_dataframe(self):
        mock_response = {
            "dataset": [
                {
                    "c_dataset": ["dec", "dhc"],
                    "title": "Demographic and Housing Characteristics",
                    "description": "2020 DHC data",
                },
                {
                    "c_dataset": ["dec", "dhc-a"],
                    "title": "DHC-A Detailed",
                    "description": "Detailed race data",
                },
                {
                    "c_dataset": ["acs", "acs5"],
                    "title": "ACS 5-Year",
                    "description": "ACS data (not decennial)",
                },
            ]
        }
        with patch("pypums.census_helpers._fetch_json", return_value=mock_response):
            df = summary_files(year=2020)
        assert isinstance(df, pd.DataFrame)
        # Only decennial datasets should be included.
        assert len(df) == 2

    def test_columns(self):
        mock_response = {
            "dataset": [
                {
                    "c_dataset": ["dec", "dhc"],
                    "title": "DHC",
                    "description": "Test",
                },
            ]
        }
        with patch("pypums.census_helpers._fetch_json", return_value=mock_response):
            df = summary_files(year=2020)
        for col in ("dataset_name", "title", "description"):
            assert col in df.columns

    def test_empty_response(self):
        with patch("pypums.census_helpers._fetch_json", return_value={"dataset": []}):
            df = summary_files(year=2020)
        assert len(df) == 0


class TestGetPopGroups:
    """Tests for get_pop_groups()."""

    def test_returns_dataframe(self):
        mock_response = [
            ["POP_GROUP", "POP_GROUP_NAME"],
            ["0001", "Total population"],
            ["0002", "Hispanic or Latino"],
            ["0003", "White alone"],
        ]
        with patch("pypums.census_helpers._fetch_json", return_value=mock_response):
            df = get_pop_groups(year=2020)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_columns(self):
        mock_response = [
            ["POP_GROUP", "POP_GROUP_NAME"],
            ["0001", "Total population"],
        ]
        with patch("pypums.census_helpers._fetch_json", return_value=mock_response):
            df = get_pop_groups(year=2020)
        assert "code" in df.columns
        assert "label" in df.columns

    def test_empty_response(self):
        with patch("pypums.census_helpers._fetch_json", return_value=[]):
            df = get_pop_groups(year=2020)
        assert len(df) == 0
