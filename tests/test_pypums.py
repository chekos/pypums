import pytest
from pandas import DataFrame

from pypums import ACS
from pypums.utils import _clean_year, build_acs_url, data_dir


def test_build_acs_url():
    assert (
        build_acs_url()
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2023/1-Year/csv_pca.zip"
    )
    assert (
        build_acs_url(
            year=2005, survey="1-year", sample_unit="household", state="arkansas"
        )
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2005/csv_har.zip"
    )
    assert (
        build_acs_url(
            year=2012, survey="3-year", sample_unit="person", state="Delaware"
        )
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2012/3-Year/csv_pde.zip"
    )
    assert (
        build_acs_url(2018, "3-year", "household", "colorado")
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/5-Year/csv_hco.zip"
    )


def test_build_acs_url_2020():
    """2020 only has 5-Year data due to COVID-19."""
    assert (
        build_acs_url(year=2020, survey="1-year", sample_unit="person", state="Ohio")
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2020/5-Year/csv_poh.zip"
    )
    assert (
        build_acs_url(year=2020, survey="5-year", sample_unit="person", state="Ohio")
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2020/5-Year/csv_poh.zip"
    )


def test_build_acs_url_post_2019():
    """Years 2021-2024 should work with 1-Year and 5-Year surveys."""
    assert (
        build_acs_url(year=2022, survey="1-year", sample_unit="person", state="Texas")
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2022/1-Year/csv_ptx.zip"
    )
    assert (
        build_acs_url(
            year=2024, survey="5-year", sample_unit="household", state="New York"
        )
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2024/5-Year/csv_hny.zip"
    )


def test_clean_year_range():
    """_clean_year accepts 2000-2024 and two-digit shortcuts 0-24."""
    assert _clean_year(2000) == 2000
    assert _clean_year(2024) == 2024
    assert _clean_year(0) == 2000
    assert _clean_year(24) == 2024
    assert _clean_year(23) == 2023

    with pytest.raises(ValueError, match="2000 and 2024"):
        _clean_year(2025)
    with pytest.raises(ValueError, match="2000 and 2024"):
        _clean_year(1999)


def test_acs_class_urls():
    assert (
        ACS()._survey_url
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2023/1-Year/csv_pca.zip"
    )
    assert (
        ACS(2005, "arkansas", "1-year", "household")._survey_url
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2005/csv_har.zip"
    )
    assert (
        ACS(2012, "Delaware", "3-year", "person")._survey_url
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2012/3-Year/csv_pde.zip"
    )
    assert (
        ACS(2018, "colorado", "3-year", "household")._survey_url
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/5-Year/csv_hco.zip"
    )


def test_acs_class_2020():
    """ACS for 2020 should always use 5-Year survey."""
    acs_2020 = ACS(2020, "Ohio", "1-Year")
    assert acs_2020._survey == "5-Year/"
    assert (
        acs_2020._survey_url
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2020/5-Year/csv_poh.zip"
    )


def test_acs_class_attributes():
    assert ACS()._sample_unit == ACS().sample_unit[0].lower()
    assert ACS(sample_unit="household")._sample_unit == "h"
    assert ACS(2018, survey="3-Year")._survey == "5-Year/"
    assert ACS(state="cloroado")._state_abbr == "co"
    assert ACS(2020, survey="1-Year")._survey == "5-Year/"


def test_acs_class_as_df():
    assert isinstance(ACS(state="alaska").as_dataframe(), DataFrame)


def test_instantiated_acs():
    instantiated_ACS = ACS()
    instantiated_ACS.download()
    instantiated_df = instantiated_ACS.as_dataframe()
    assert instantiated_ACS._extracted is True
    assert instantiated_ACS._data_dir == data_dir
    assert instantiated_ACS._extract_folder == data_dir.joinpath(
        f"interim/acs_{str(instantiated_ACS._year)[-2:]}/{instantiated_ACS._state_abbr}/"
    )
    assert instantiated_ACS._download_folder == data_dir.joinpath(
        f"raw/acs_{str(instantiated_ACS._year)[-2:]}/"
    )
    assert isinstance(instantiated_df, DataFrame)
