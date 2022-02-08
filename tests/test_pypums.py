from random import sample
from pypums.utils import build_acs_url


def test_build_acs_url():
    assert (
        build_acs_url()
        == "https://www2.census.gov/programs-surveys/acs/data/pums/2018/1-Year/csv_pca.zip"
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
