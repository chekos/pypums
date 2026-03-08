"""Tests for ``to_survey()`` — survey design with replicate weights."""

import pandas as pd
import pytest

from pypums.survey import SurveyDesign, to_survey


class TestToSurvey:
    """Tests for the to_survey() function."""

    @pytest.fixture()
    def pums_df(self):
        """A minimal PUMS DataFrame with person replicate weights."""
        data = {
            "SERIALNO": ["001", "002", "003"],
            "SPORDER": [1, 1, 1],
            "PWGTP": [50, 45, 60],
            "AGEP": [35, 33, 42],
            "SEX": [1, 2, 1],
            "ST": ["06", "06", "06"],
            "PUMA": ["03701", "03701", "03701"],
        }
        # Add replicate weights (PWGTP1..PWGTP80).
        for i in range(1, 81):
            data[f"PWGTP{i}"] = [50 + i % 5, 45 + i % 3, 60 + i % 7]
        return pd.DataFrame(data)

    def test_returns_survey_design(self, pums_df):
        result = to_survey(pums_df, weight_type="person")
        assert isinstance(result, SurveyDesign)

    def test_survey_design_repr(self, pums_df):
        result = to_survey(pums_df, weight_type="person")
        repr_str = repr(result)
        assert "SurveyDesign" in repr_str
        assert "n=3" in repr_str

    def test_weighted_estimate(self, pums_df):
        design = to_survey(pums_df, weight_type="person")
        est = design.weighted_estimate("AGEP")
        # 35*50 + 33*45 + 42*60 = 1750 + 1485 + 2520 = 5755
        assert est == 5755.0

    def test_weighted_mean(self, pums_df):
        design = to_survey(pums_df, weight_type="person")
        mean = design.weighted_mean("AGEP")
        # 5755 / (50+45+60) = 5755 / 155 ≈ 37.13
        expected = 5755.0 / 155.0
        assert abs(mean - expected) < 0.01

    def test_standard_error_is_positive(self, pums_df):
        design = to_survey(pums_df, weight_type="person")
        se = design.standard_error("AGEP")
        assert se > 0

    def test_raises_on_missing_weight(self):
        df = pd.DataFrame({"AGEP": [35, 33]})
        with pytest.raises(ValueError, match="Weight column"):
            to_survey(df, weight_type="person")

    def test_raises_on_missing_rep_weights(self):
        df = pd.DataFrame({"PWGTP": [50, 45], "AGEP": [35, 33]})
        with pytest.raises(ValueError, match="No replicate weight"):
            to_survey(df, weight_type="person")

    def test_invalid_type_raises(self, pums_df):
        with pytest.raises(ValueError, match="weight_type must be"):
            to_survey(pums_df, weight_type="invalid")

    def test_invalid_design_raises(self, pums_df):
        with pytest.raises(ValueError, match="Only 'rep_weights'"):
            to_survey(pums_df, weight_type="person", design="stratified")

    def test_housing_type(self):
        """Housing type should use WGTP weights."""
        data = {
            "WGTP": [100, 200],
            "ROOMS": [5, 8],
        }
        for i in range(1, 81):
            data[f"WGTP{i}"] = [100 + i % 10, 200 + i % 10]
        df = pd.DataFrame(data)
        design = to_survey(df, weight_type="housing")
        assert design.weight == "WGTP"
        assert len(design.rep_weights) == 80
