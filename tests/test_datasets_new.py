"""Tests for new datasets: pums_variables, acs5_geography, mig_recodes."""

from unittest.mock import patch

import pandas as pd


class TestMigRecodes:
    """Tests for the mig_recodes dataset."""

    def test_mig_recodes_is_dataframe(self):
        from pypums.datasets.mig_recodes import mig_recodes

        assert isinstance(mig_recodes, pd.DataFrame)

    def test_mig_recodes_columns(self):
        from pypums.datasets.mig_recodes import mig_recodes

        assert "dimension" in mig_recodes.columns
        assert "code" in mig_recodes.columns
        assert "label" in mig_recodes.columns

    def test_mig_recodes_has_entries(self):
        from pypums.datasets.mig_recodes import mig_recodes

        assert len(mig_recodes) > 0

    def test_mig_recodes_labels_dict(self):
        from pypums.datasets.mig_recodes import MIG_RECODE_LABELS

        assert isinstance(MIG_RECODE_LABELS, dict)
        assert "SEX_GROUP" in MIG_RECODE_LABELS
        assert MIG_RECODE_LABELS["SEX_GROUP"]["1"] == "Male"


class TestPumsVariables:
    """Tests for the pums_variables dataset function."""

    def test_returns_dataframe(self):
        from pypums.datasets.pums_vars import pums_variables

        mock_response = {
            "variables": {
                "AGEP": {
                    "label": "Age",
                    "concept": "Demographics",
                    "predicateType": "int",
                },
                "SEX": {
                    "label": "Sex",
                    "concept": "Demographics",
                    "predicateType": "int",
                },
            }
        }
        with patch(
            "pypums.datasets.pums_vars._fetch_pums_variables_json",
            return_value=mock_response,
        ):
            df = pums_variables(cache=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_has_expected_columns(self):
        from pypums.datasets.pums_vars import pums_variables

        mock_response = {
            "variables": {
                "AGEP": {
                    "label": "Age",
                    "concept": "Demographics",
                    "predicateType": "int",
                },
            }
        }
        with patch(
            "pypums.datasets.pums_vars._fetch_pums_variables_json",
            return_value=mock_response,
        ):
            df = pums_variables(cache=False)
        for col in ("name", "label", "concept", "var_type"):
            assert col in df.columns


class TestAcs5Geography:
    """Tests for the acs5_geography dataset function."""

    def test_returns_dataframe(self):
        from pypums.datasets.acs5_geography import acs5_geography

        mock_response = {
            "fips": [
                {
                    "name": "state",
                    "geoLevelDisplay": "040",
                    "requires": [],
                },
                {
                    "name": "county",
                    "geoLevelDisplay": "050",
                    "requires": [{"name": "state"}],
                },
            ]
        }
        with patch(
            "pypums.datasets.acs5_geography._fetch_geography_json",
            return_value=mock_response,
        ):
            df = acs5_geography(cache=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_has_expected_columns(self):
        from pypums.datasets.acs5_geography import acs5_geography

        mock_response = {
            "fips": [
                {
                    "name": "state",
                    "geoLevelDisplay": "040",
                    "requires": [],
                },
            ]
        }
        with patch(
            "pypums.datasets.acs5_geography._fetch_geography_json",
            return_value=mock_response,
        ):
            df = acs5_geography(cache=False)
        for col in ("name", "hierarchy", "requires"):
            assert col in df.columns
