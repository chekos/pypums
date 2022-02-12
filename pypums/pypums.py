"""Main PyPUMS module."""

from pypums.utils import _download_data, build_acs_url


def get_data(
    year: int = 2018,
    survey: str = "1-Year",
    sample_unit: str = "person",
    state: str = "California",
    data_directory: str = "../data/",
    extract: bool = True,
) -> None:
    """
    Downloads ACS 1-Year or 5-Year state PUMS estimates into a specified folder (defaults to `../data/`).
    """

    # builds URL
    URL = build_acs_url(
        year=year,
        survey=survey,
        sample_unit=sample_unit,
        state=state,
    )

    # download data
    _download_data(
        url=URL,
        year=year,
        name="ACS",
        state=state,
        extract=extract,
        data_directory=data_directory,
    )

    return None


if __name__ == "__main__":
    get_data()
