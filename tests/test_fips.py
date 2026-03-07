"""Tests for the built-in FIPS codes dataset.

Phase 0 — Foundation.

The ``fips_codes`` dataset should be a pandas DataFrame bundling every
US state and county FIPS code, mirroring the ``fips_codes`` tibble shipped
with tidycensus.
"""

import pandas as pd
import pytest

from pypums.datasets import fips_codes

pytestmark = pytest.mark.phase0


def test_fips_codes_is_dataframe():
    """``fips_codes`` is a pandas DataFrame."""
    assert isinstance(fips_codes, pd.DataFrame)


def test_fips_codes_has_expected_columns():
    """Must include at minimum these identifier columns."""
    for col in ("state", "state_code", "county", "county_code"):
        assert col in fips_codes.columns, f"Missing column: {col}"


def test_fips_codes_has_all_states():
    """All 50 states + DC should be present."""
    states = fips_codes["state"].unique()
    assert len(states) >= 51  # 50 states + DC at minimum


def test_fips_lookup_california():
    """Can look up California by name and get FIPS code '06'."""
    ca = fips_codes[fips_codes["state"] == "California"]
    assert not ca.empty
    assert ca["state_code"].iloc[0] == "06"
