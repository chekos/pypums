"""Tests for ``get_survey_metadata()`` — Census dataset discovery.

Phase 4 — Survey metadata.

These tests define the contract for ``get_survey_metadata()``:

* Returns a DataFrame with expected columns.
* ``year`` parameter filters results by vintage.
* All datasets are returned when no year is specified.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from pypums import get_survey_metadata


# Sample data.json response for testing.
@pytest.fixture()
def data_json_response():
    return {
        "dataset": [
            {
                "title": "American Community Survey 5-Year Data",
                "description": "ACS 5-year estimates",
                "c_vintage": 2023,
                "c_dataset": ["acs", "acs5"],
                "distribution": [
                    {"accessURL": "https://api.census.gov/data/2023/acs/acs5"}
                ],
            },
            {
                "title": "American Community Survey 1-Year Data",
                "description": "ACS 1-year estimates",
                "c_vintage": 2023,
                "c_dataset": ["acs", "acs1"],
                "distribution": [
                    {"accessURL": "https://api.census.gov/data/2023/acs/acs1"}
                ],
            },
            {
                "title": "Decennial Census",
                "description": "2020 Decennial Census",
                "c_vintage": 2020,
                "c_dataset": ["dec", "dhc"],
                "distribution": [
                    {"accessURL": "https://api.census.gov/data/2020/dec/dhc"}
                ],
            },
            {
                "title": "Population Estimates",
                "description": "PEP population",
                "c_vintage": 2022,
                "c_dataset": ["pep", "population"],
                "distribution": [
                    {"accessURL": "https://api.census.gov/data/2022/pep/population"}
                ],
            },
        ]
    }


def _mock_fetch(data_json_response):
    return patch(
        "pypums.survey._fetch_data_json",
        return_value=data_json_response,
    )


class TestGetSurveyMetadataReturnType:
    def test_returns_dataframe(self, data_json_response):
        with _mock_fetch(data_json_response):
            df = get_survey_metadata()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_expected_columns(self, data_json_response):
        with _mock_fetch(data_json_response):
            df = get_survey_metadata()
        for col in (
            "title",
            "description",
            "vintage",
            "dataset_name",
            "distribution_url",
        ):
            assert col in df.columns, f"Missing column: {col}"


class TestGetSurveyMetadataFiltering:
    def test_all_datasets_without_year(self, data_json_response):
        """Without year filter, all datasets are returned."""
        with _mock_fetch(data_json_response):
            df = get_survey_metadata()
        assert len(df) == 4

    def test_filter_by_year(self, data_json_response):
        """year parameter filters to matching vintage."""
        with _mock_fetch(data_json_response):
            df = get_survey_metadata(year=2023)
        assert len(df) == 2
        assert all(df["vintage"] == 2023)

    def test_filter_by_year_no_results(self, data_json_response):
        """Filtering by a year with no data returns empty DataFrame."""
        with _mock_fetch(data_json_response):
            df = get_survey_metadata(year=1999)
        assert len(df) == 0


class TestGetSurveyMetadataContent:
    def test_dataset_name_built_from_c_dataset(self, data_json_response):
        """dataset_name should be built by joining c_dataset list."""
        with _mock_fetch(data_json_response):
            df = get_survey_metadata(year=2023)
        names = set(df["dataset_name"])
        assert "acs/acs5" in names
        assert "acs/acs1" in names

    def test_distribution_url_populated(self, data_json_response):
        """distribution_url should be populated from the distribution field."""
        with _mock_fetch(data_json_response):
            df = get_survey_metadata(year=2020)
        assert (
            df["distribution_url"].iloc[0] == "https://api.census.gov/data/2020/dec/dhc"
        )

    def test_vintage_is_integer(self, data_json_response):
        """vintage column should be integer type."""
        with _mock_fetch(data_json_response):
            df = get_survey_metadata()
        # Filter to non-null vintages
        non_null = df[df["vintage"].notna()]
        assert all(isinstance(v, int) for v in non_null["vintage"])
