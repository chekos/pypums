"""Tests for ``breakdown_labels`` in estimates and flows."""

from unittest.mock import patch

import pytest

from pypums import get_estimates, get_flows

pytestmark = pytest.mark.phase3


class TestEstimatesBreakdownLabels:
    """Tests for breakdown_labels in get_estimates()."""

    def test_breakdown_labels_adds_label_column(self, fake_api_key):
        """breakdown_labels=True should add *_label columns."""
        response = [
            ["NAME", "POP", "AGEGROUP", "SEX", "state"],
            ["California", "38965193", "0", "0", "06"],
            ["California", "19000000", "0", "1", "06"],
            ["California", "19965193", "0", "2", "06"],
        ]
        with patch("pypums.estimates._call_census_api", return_value=response):
            df = get_estimates(
                geography="state",
                product="characteristics",
                variables=["POP"],
                breakdown=["AGEGROUP", "SEX"],
                breakdown_labels=True,
                key=fake_api_key,
            )
        assert "AGEGROUP_label" in df.columns
        assert "SEX_label" in df.columns

    def test_breakdown_labels_correct_values(self, fake_api_key):
        """Label values should match the lookup table."""
        response = [
            ["NAME", "POP", "SEX", "state"],
            ["California", "19000000", "1", "06"],
            ["California", "19965193", "2", "06"],
        ]
        with patch("pypums.estimates._call_census_api", return_value=response):
            df = get_estimates(
                geography="state",
                product="characteristics",
                variables=["POP"],
                breakdown=["SEX"],
                breakdown_labels=True,
                output="wide",
                key=fake_api_key,
            )
        labels = df["SEX_label"].tolist()
        assert "Male" in labels
        assert "Female" in labels

    def test_breakdown_labels_false_no_label_columns(self, fake_api_key):
        """breakdown_labels=False should not add label columns."""
        response = [
            ["NAME", "POP", "SEX", "state"],
            ["California", "19000000", "1", "06"],
        ]
        with patch("pypums.estimates._call_census_api", return_value=response):
            df = get_estimates(
                geography="state",
                product="characteristics",
                variables=["POP"],
                breakdown=["SEX"],
                breakdown_labels=False,
                output="wide",
                key=fake_api_key,
            )
        assert "SEX_label" not in df.columns


class TestFlowsBreakdownLabels:
    """Tests for breakdown_labels in get_flows()."""

    def test_breakdown_labels_adds_label_column(self, fake_api_key):
        """breakdown_labels=True should add *_label columns for flows."""
        response = [
            [
                "FULL1_NAME",
                "FULL2_NAME",
                "MOVEDIN",
                "MOVEDIN_M",
                "MOVEDOUT",
                "MOVEDOUT_M",
                "MOVEDNET",
                "MOVEDNET_M",
                "SEX_GROUP",
                "state1",
                "county1",
                "state2",
                "county2",
            ],
            [
                "Los Angeles County, California",
                "Maricopa County, Arizona",
                "15234",
                "1200",
                "22456",
                "1500",
                "-7222",
                "1921",
                "1",
                "06",
                "037",
                "04",
                "013",
            ],
        ]
        with patch("pypums.flows._call_census_api", return_value=response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                breakdown=["SEX_GROUP"],
                breakdown_labels=True,
                output="wide",
                key=fake_api_key,
            )
        assert "SEX_GROUP_label" in df.columns
        assert df["SEX_GROUP_label"].iloc[0] == "Male"

    def test_breakdown_labels_false_no_labels(self, flows_api_response, fake_api_key):
        """breakdown_labels=False should not add label columns."""
        with patch("pypums.flows._call_census_api", return_value=flows_api_response):
            df = get_flows(
                geography="county",
                state="CA",
                county="037",
                breakdown_labels=False,
                output="wide",
                key=fake_api_key,
            )
        label_cols = [c for c in df.columns if c.endswith("_label")]
        assert len(label_cols) == 0
