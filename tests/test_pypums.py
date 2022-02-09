from pypums.utils import build_acs_url
from pypums import ACS


def test_build_acs_url():
    assert (
        build_acs_url()
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/1-year/csv_pca.zip"
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
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2012/3-year/csv_pde.zip"
    )
    assert (
        build_acs_url(2018, "3-year", "household", "colorado")
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/5-year/csv_hco.zip"
    )


def test_acs_class_urls():
    assert (
        ACS()._SURVEY_URL
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/1-year/csv_pca.zip"
    )
    assert (
        ACS(2005, "arkansas", "1-year", "household")._SURVEY_URL
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2005/csv_har.zip"
    )
    assert (
        ACS(2012, "Delaware", "3-year", "person")._SURVEY_URL
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2012/3-year/csv_pde.zip"
    )
    assert (
        ACS(2018, "colorado", "3-year", "household")._SURVEY_URL
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/5-year/csv_hco.zip"
    )


def test_acs_class_attributes():
    assert ACS()._sample_unit == ACS().sample_unit[0].lower()
    assert ACS(sample_unit="household")._sample_unit == "h"
    assert ACS(2018, survey="3-Year")._survey == "5-year/"
    assert ACS(state="cloroado")._state_abbr == "co"
