"""Shared fixtures for pypums test suite.

Provides mock Census API responses, fake API keys, and temporary
cache directories used across all test files.
"""

import pytest


@pytest.fixture()
def fake_api_key():
    """A fake Census API key for testing."""
    return "fake_test_key_0123456789abcdef"


@pytest.fixture()
def cache_dir(tmp_path):
    """Temporary cache directory for testing."""
    d = tmp_path / "cache"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Sample Census API JSON responses
# These mirror the structure returned by api.census.gov so we can mock httpx
# calls and still test DataFrame construction, column naming, etc.
# ---------------------------------------------------------------------------

@pytest.fixture()
def acs_api_response_tidy():
    """Sample ACS API response (JSON rows) for 2 variables, 2 counties."""
    return [
        ["NAME", "B01001_001E", "B01001_001M", "B02001_002E", "B02001_002M", "state", "county"],
        ["Los Angeles County, California", "10014009", "0", "2786755", "9012", "06", "037"],
        ["Orange County, California", "3186989", "0", "1298431", "6234", "06", "059"],
    ]


@pytest.fixture()
def decennial_api_response():
    """Sample Decennial Census API response for 2 variables, 2 states."""
    return [
        ["NAME", "P1_001N", "P1_002N", "state"],
        ["California", "39538223", "39538223", "06"],
        ["Texas", "29145505", "29145505", "48"],
    ]


@pytest.fixture()
def variables_api_response():
    """Sample variables endpoint response."""
    return {
        "variables": {
            "B01001_001E": {
                "label": "Estimate!!Total:",
                "concept": "SEX BY AGE",
                "predicateType": "int",
                "group": "B01001",
            },
            "B01001_002E": {
                "label": "Estimate!!Total:!!Male:",
                "concept": "SEX BY AGE",
                "predicateType": "int",
                "group": "B01001",
            },
        }
    }


@pytest.fixture()
def pums_api_response():
    """Sample PUMS API response with person-level records."""
    return [
        ["SERIALNO", "SPORDER", "PWGTP", "AGEP", "SEX", "ST", "PUMA"],
        ["2023HU0000001", "01", "50", "35", "1", "06", "03701"],
        ["2023HU0000001", "02", "45", "33", "2", "06", "03701"],
        ["2023HU0000002", "01", "60", "42", "1", "06", "03701"],
    ]


@pytest.fixture()
def estimates_api_response():
    """Sample Population Estimates API response."""
    return [
        ["NAME", "POP_2023", "DENSITY_2023", "state"],
        ["California", "38965193", "254.3", "06"],
        ["Texas", "30503301", "117.3", "48"],
    ]


@pytest.fixture()
def flows_api_response():
    """Sample ACS Migration Flows API response."""
    return [
        [
            "FULL1_NAME", "FULL2_NAME",
            "MOVEDIN", "MOVEDIN_M",
            "MOVEDOUT", "MOVEDOUT_M",
            "MOVEDNET", "MOVEDNET_M",
            "state1", "county1", "state2", "county2",
        ],
        [
            "Los Angeles County, California",
            "Maricopa County, Arizona",
            "15234", "1200", "22456", "1500", "-7222", "1921",
            "06", "037", "04", "013",
        ],
    ]
